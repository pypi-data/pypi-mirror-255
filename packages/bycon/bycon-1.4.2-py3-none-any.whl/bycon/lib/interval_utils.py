import numpy as np
from copy import deepcopy

from genome_utils import *

################################################################################

"""
The methods here address genomic binning, the assignment of sample-specific
bin values (e.g. CNV overlap, maximum/minimum observed value in the bin...) as
well as the calculation of bin statistics.

The methods rely on the existence of cytoband files which contain information
about the individual chromosomes (size, centromere position as indicated by
the transition from p- to q-arm). The bins then can be generated directly
corresponding to the listed cytobands or (the default) by producing equally
sized bins (default 1Mb). The most distal bin of each arm then can be of a
different size.

Bin sizes are selected based on the provided key for a corresponding definition
in `interval_definitions.genome_bin_sizes` (e.g. 1Mb => 1000000).

### Interval Object Schema

```
no:
  description: counter, from 1pter -> Yqter (or whatever chromosomes are provided)
  type: integer
id:
  description: the id/label of the interval, from concatenating chromosome and base range
  type: string
reference_name:
  description: the chromosome as provided in the cytoband file
  type: string
  examples:
    - 7
    - Y
arm:
  type: string
  examples:
    - p
    - q
cytobands:
  type: string
  examples:
    - 1p12.1
start:
  description: the 0/interbase start of the interval
  type: integer
end:
  description: the 0/interbase end of the interval
  type: integer
```
"""

################################################################################
################################################################################
################################################################################

def generate_genomic_mappings(byc):
    parse_refseq_file(byc)
    translate_reference_ids(byc)
    parse_cytoband_file(byc)
    __generate_cytoband_intervals(byc)
    __generate_genomic_intervals(byc)
    byc.update({"genomic_interval_count": len(byc["genomic_intervals"])})


################################################################################

def __generate_genomic_intervals(byc):

    i_d = byc["interval_definitions"]
    g_b_s = i_d["genome_bin_sizes"].get("values", {})
    binning = byc["form_data"].get("genome_binning", i_d["genome_binning"])
    i_d.update({"genome_binning": binning})

    # cytobands ################################################################

    if binning == "cytobands":
        byc.update({"genomic_intervals": deepcopy(byc["cytoband_intervals"])})
        return

    # otherwise intervals ######################################################

    c_l = byc["cytolimits"]

    assert binning in i_d["genome_bin_sizes"]["values"].keys(), f'¡¡ Binning value "{binning}" not in list !!'

    int_b = i_d["genome_bin_sizes"]["values"][binning]
    e_p_f = i_d["terminal_intervals_soft_expansion_fraction"].get("value", 0.1)
    e_p = int_b * e_p_f

    intervals = []
    i = 1

    for chro in c_l.keys():

        p_max = c_l[chro]["p"][-1]
        q_max = c_l[chro]["size"]
        arm = "p"
        start = 0

        # calculate first interval to end p-arm with a full sized one
        p_first = p_max
        while p_first >= int_b + e_p:
            p_first -= int_b

        end = start + p_first
        while start < q_max:
            int_p = int_b
            if end > q_max:
                end = q_max
            elif q_max < end + e_p:
                end = q_max
                int_p += e_p
            if end >= p_max:
                arm = "q"
            size = end - start

            intervals.append({
                "no": i,
                "id": f'{chro}{arm}:{start}-{end}',
                "reference_name": chro,
                "arm": arm,
                "cytobands": f'{chro}{cytobands_label_from_positions(byc, chro, start, end)}',
                "start": start,
                "end": end,
                "size": size
            })

            start = end
            end += int_p
            i += 1

    byc.update({"genomic_intervals": intervals})


################################################################################

def __generate_cytoband_intervals(byc):
    intervals = []

    for cb in byc["cytobands"]:
        intervals.append({
            "no": int(cb["i"]),
            "id": "{}:{}-{}".format(cb["chro"], cb["start"], cb["end"]),
            "reference_name": cb["chro"],
            "cytobands": cb["cytoband"],
            "start": int(cb["start"]),
            "end": int(cb["end"]),
            "size": int(cb["end"]) - int(cb["start"])
        })

    byc.update({"cytoband_intervals": intervals})


################################################################################

def interval_cnv_arrays(cs_vars, byc):
    """
    The method generates sample-specific CNV maps using the currently defined
    interval bins. The output (`cnv_statusmaps`) provides annotated intervals
    for overlap fractions (`cnv_statusmaps.dup`, `cnv_statusmaps.del`) as well
    as the minimum and maximum values observed in those intervals
    (`cnv_statusmaps.max`, `cnv_statusmaps.min`).
    """

    # TODO: make this a class to split out the stats etc.

    g_b = byc["interval_definitions"].get("genome_binning", "")

    v_t_defs = byc["variant_type_definitions"]
    c_l = byc["cytolimits"]
    intervals = byc["genomic_intervals"]

    cov_labs = {"DUP": 'dup', "DEL": 'del'}
    val_labs = {"DUP": 'max', "DEL": 'min'}

    int_no = len(intervals)

    maps = {
        "interval_count": int_no,
        "binning": g_b
    }

    for cov_lab in cov_labs.values():
        maps.update({cov_lab: [0 for i in range(int_no)]})
    for val_lab in val_labs.values():
        maps.update({val_lab: [0 for i in range(int_no)]})

    cnv_stats = {
        "cnvcoverage": 0,
        "dupcoverage": 0,
        "delcoverage": 0,
        "cnvfraction": 0,
        "dupfraction": 0,
        "delfraction": 0
    }

    chro_stats = {}

    for chro in c_l.keys():
        chro_stats.update({chro: deepcopy(cnv_stats)})
        for arm in ['p', 'q']:
            c_a = chro + arm
            chro_stats.update({c_a: deepcopy(cnv_stats)})

    # cs_vars = v_coll.find( query )
    if type(cs_vars).__name__ == "Cursor":
        cs_vars.rewind()
    v_no = len(list(cs_vars))

    if v_no < 1:
        return maps, cnv_stats, chro_stats

    # the values_map collects all values for the given interval to retrieve
    # the min and max values of each interval
    values_map = [[] for i in range(int_no)]

    digests = []

    if type(cs_vars).__name__ == "Cursor":
        cs_vars.rewind()

    for v in cs_vars:
        if "variant_state" not in v:
            continue

        v_t_c = v["variant_state"].get("id", "__NA__")
        if v_t_c not in v_t_defs.keys():
            continue

        dup_del = v_t_defs[v_t_c].get("DUPDEL")
        # skipping non-CNV vars
        if dup_del is None:
            continue

        cov_lab = cov_labs[dup_del]

        if "reference_name" not in v:
            v.update({"reference_name": v["location"]["chromosome"]})

        v_i_id = v.get("variant_internal_id", None)
        v_cs_id = v.get("callset_id", None)

        if v_i_id in digests:
            if "local" in byc["env"]:
                print("¡¡¡ {} already counted for {}".format(v_i_id, v_cs_id))
        else:
            digests.append(v_i_id)

        for i, intv in enumerate(intervals):

            if _has_overlap(intv, v):

                ov_end = min(intv["end"], v["location"]["end"])
                ov_start = max(intv["start"], v["location"]["start"])
                ov = ov_end - ov_start
                maps[cov_lab][i] += ov

                try:
                    # print(type(v["info"]["cnv_value"]))
                    if type(v["info"]["cnv_value"]) == int or type(v["info"]["cnv_value"]) == float:
                        values_map[i].append(v["info"]["cnv_value"])
                    else:
                        values_map[i].append(v_t_defs[v_t_c].get("cnv_dummy_value"))
                except Exception:
                    pass

    # statistics
    for cov_lab in cov_labs.values():
        for i, intv in enumerate(intervals):
            if maps[cov_lab][i] > 0:
                cov = maps[cov_lab][i]
                lab = f'{cov_lab}coverage'
                chro = str(intv["reference_name"])
                c_a = chro + intv["arm"]
                cnv_stats[lab] += cov
                chro_stats[chro][lab] += cov
                chro_stats[c_a][lab] += cov
                cnv_stats["cnvcoverage"] += cov
                chro_stats[chro]["cnvcoverage"] += cov
                chro_stats[c_a]["cnvcoverage"] += cov
                maps[cov_lab][i] = round(maps[cov_lab][i] / intervals[i]["size"], 3)

    for s_k in cnv_stats.keys():
        if "coverage" in s_k:
            f_k = re.sub("coverage", "fraction", s_k)
            cnv_stats.update({s_k: int(cnv_stats[s_k])})
            cnv_stats.update({f_k: _round_frac(cnv_stats[s_k], byc["genome_size"], 3)})

            for chro in c_l.keys():
                chro_stats[chro].update({s_k: int(chro_stats[chro][s_k])})
                chro_stats[chro].update(
                    {f_k: _round_frac(chro_stats[chro][s_k], c_l[chro]['size'], 3)})
                for arm in ['p', 'q']:
                    c_a = chro + arm
                    s_a = c_l[chro][arm][-1] - c_l[chro][arm][0]
                    chro_stats[c_a].update({s_k: int(chro_stats[c_a][s_k])})
                    chro_stats[c_a].update(
                        {f_k: _round_frac(chro_stats[c_a][s_k], s_a, 3)})

    # the values for each interval are sorted, to allow extracting the min/max 
    # values by position
    # the last of the sorted values is assigned if > 0
    for i in range(len(values_map)):
        if values_map[i]:
            values_map[i].sort()
            if values_map[i][-1] > 0:
                maps["max"][i] = round(values_map[i][-1], 3)
            if values_map[i][0] < 0:
                maps["min"][i] = round(values_map[i][0], 3)

    return maps, cnv_stats, chro_stats


################################################################################

def _round_frac(val, maxval, digits=3):
    f = round(val / maxval, digits)
    if f > 1:
        f = 1
    return f


################################################################################

def interval_counts_from_callsets(callsets, byc):
    """
    This method will analyze a set (either list or MongoDB Cursor) of Progenetix
    callsets with CNV statusmaps and return a list of standard genomic interval
    objects with added per-interval quantitative data.
    """

    min_f = byc["interval_definitions"]["interval_min_fraction"].get("value", 0.001)
    int_fs = deepcopy(byc["genomic_intervals"])
    int_no = len(int_fs)

    # callsets can be either a list or a MongoDB Cursor (which has to be re-set)
    if type(callsets).__name__ == "Cursor":
        callsets.rewind()

    cs_no = len(list(callsets))
    f_factor = 0

    if cs_no > 0:
        f_factor = 100 / cs_no

    pars = {
        "gain": {"cov_l": "dup", "val_l": "max"},
        "loss": {"cov_l": "del", "val_l": "min"}
    }

    for t in pars.keys():

        covs = np.zeros((cs_no, int_no))
        vals = np.zeros((cs_no, int_no))

        if type(callsets).__name__ == "Cursor":
            callsets.rewind()

        for i, cs in enumerate(callsets):
            covs[i] = cs["cnv_statusmaps"][pars[t]["cov_l"]]
            vals[i] = cs["cnv_statusmaps"][pars[t]["val_l"]]

        counts = np.count_nonzero(covs >= min_f, axis=0)
        frequencies = np.around(counts * f_factor, 3)
        medians = np.around(np.ma.median(np.ma.masked_where(covs < min_f, vals), axis=0).filled(0), 3)
        means = np.around(np.ma.mean(np.ma.masked_where(covs < min_f, vals), axis=0).filled(0), 3)

        for i, interval in enumerate(int_fs):
            int_fs[i].update({
                t + "_frequency": frequencies[i],
                t + "_median": medians[i],
                t + "_mean": means[i]
            })

    if type(callsets).__name__ == "Cursor":
        callsets.close()

    return int_fs, cs_no


################################################################################

def _has_overlap(interval, v):
    if not interval["reference_name"] == v["reference_name"]:
        return False

    if not interval["end"] > v["location"]["start"]:
        return False

    if not interval["start"] < v["location"]["end"]:
        return False

    return True


################################################################################
