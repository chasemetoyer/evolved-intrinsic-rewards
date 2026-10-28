"""Generate paper/numbers.tex and paper/data/numbers.json.

Every measured or computed value quoted in the prose of main.tex is a macro \\val{key} defined here. Each value is
read from the source snapshots in paper/data/sources (scored JSON files, consolidated-results.md, round reports) or
from the post-hoc data in paper/data (bound check, run series, run records). Each key records its provenance.
check_numbers.py regenerates this output and fails on any difference, and it also scans main.tex for literal numbers.

Usage (repo root): uv run --isolated --no-project --with numpy --with scipy python paper/scripts/make_numbers.py
"""
import json, re, sys, tomllib
from pathlib import Path
import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "paper"
SRC, DATA = P / "data" / "sources", P / "data"


def J(path):
    return json.loads(Path(path).read_text())


def fp(p):
    """p-value formatting, mirroring build_consolidated.py: 2 significant digits below 0.001, else 3 decimals."""
    if p is None:
        return "--"
    if p < 0.001:
        s = f"{p:.2g}"
        if "e" not in s:
            return s
        m, e = s.split("e")
        return rf"${m}\times10^{{{int(e)}}}$"
    return f"{p:.3f}"


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def ci(k, n):
    lo, hi = cp(k, n)
    return f"[{lo:.2f}, {hi:.2f}]"


def neg(s):
    return s.replace("-", "$-$")


def comma(x):
    return f"{int(round(x)):,}"


def kfmt(x):
    """Steps in thousands, e.g. 137k."""
    return f"{int(round(x / 1000))}k"


V = {}


def put(key, text, src):
    assert key not in V, key
    V[key] = (str(text), src)


D0_ = 0.75


def main():
    r2 = J(SRC / "round2-prediction-results.json")
    r3 = J(SRC / "round3-scores.json")
    race = J(SRC / "race-results.json")
    vi3 = J(SRC / "value-iteration-results.json")
    r4 = J(SRC / "round4-scores.json")
    b0 = J(SRC / "b0-value-iteration.json")
    r5 = J(SRC / "round5-scores.json")
    pd = J(SRC / "part-d-results.json")
    s0 = J(SRC / "step0-tamper-cost.json")
    rep = J(SRC / "round2-replay-n6.json")
    a2m = J(SRC / "a2-matching.json")
    bc = J(DATA / "bound-check.json")
    bs = J(DATA / "bound-summary.json")
    rs = J(DATA / "run-series.json")
    R4, R5 = r4["runs"], r5["runs"]
    preds4 = {x["id"]: x for x in r4["predictions"]}
    preds5 = {x["id"]: x for x in r5["predictions"]}

    # ---------------------------------------------------------------- consolidated tallies
    cons = (SRC / "consolidated-results.md").read_text()
    rows = [l for l in cons.splitlines() if re.match(r"^\| [2-5] \|", l)]
    res = [l.rstrip(" |").split("|")[-1].strip() for l in rows]
    put("cons.rows", len(rows), "consolidated-results.md, rows")
    put("cons.hits", res.count("hit"), "consolidated-results.md, Result = hit")
    put("cons.misses", res.count("miss"), "consolidated-results.md, Result = miss")
    put("cons.unres", sum(r.startswith("unresolvable") for r in res), "consolidated-results.md, unresolvable")
    m = re.search(r"\*\*Totals:\*\* (\d+) pre-registered rows: (\d+) hits, (\d+) misses, (\d+) unresolvable", cons)
    assert tuple(int(x) for x in m.groups()) == (len(rows), res.count("hit"), res.count("miss"),
                                                   sum(r.startswith("unresolvable") for r in res)), "totals line disagrees"
    ncorr = len(re.findall(r"^\d+\. \*\*", cons.split("## Known misclassifications and corrections")[1], re.M))
    put("cons.ncorr", ncorr, "consolidated-results.md, corrections list")

    # ---------------------------------------------------------------- C1: wireheading, DoorKey round 4
    cat = lambda d: d["categories"]
    for k in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A1a", "A1b", "A1c", "A2a", "A2b", "A2c"):
        d = R4[k]
        put(f"r4.solve.{k}", f"{cat(d)['solve']}/{d['n']}", f"round4-scores.json runs.{k}.categories.solve")
        put(f"r4.farm.{k}", f"{cat(d)['cycle-farm']}/{d['n']}", f"round4-scores.json runs.{k}.categories.cycle-farm")
        put(f"r4.prolong.{k}", f"{cat(d)['prolong']}/{d['n']}", f"round4-scores.json runs.{k}.categories.prolong")
    on = sum(cat(R4[k])["solve"] for k in ("B1", "B2", "B3", "B4"))
    off = sum(cat(R4[k])["solve"] for k in ("A1b", "B7", "B5", "B6"))
    put("r4.solve.on", f"{on}/80", "round4-scores.json, B1-B4 solves summed")
    put("r4.solve.off", f"{off}/80", "round4-scores.json, A1b+B7+B5+B6 solves summed")
    for t in ("PB2-B1", "PB2-B2", "PB2-B3", "PB2-B4", "PB4", "PB3-B1", "PB3-B3", "A1-P1", "A1-P2",
              "A2-P1", "A2-P2", "A2-P3", "A2-P4", "A2-P5", "A2-P6", "A2-P7", "A2-P8", "PB1-pooled", "PB5"):
        put(f"p.{t}", fp(preds4[t]["p"]), f"round4-scores.json predictions[{t}].p")
        if preds4[t].get("p_holm") is not None:
            put(f"ph.{t}", fp(preds4[t]["p_holm"]), f"round4-scores.json predictions[{t}].p_holm")
    loops = [R4[k]["looper"] for k in ("B1", "B2", "B3", "B4")]
    tams = [R4[k]["tamperer"] for k in ("B1", "B2", "B3", "B4")]
    put("r4.tamperers.on", f"{sum(tams)}/80", "round4-scores.json B1-B4 tamperer")
    put("r4.loopers.on", f"{sum(loops)}/80", "round4-scores.json B1-B4 looper")
    for k in ("B1", "B3"):
        sv = [s for s in R4[k]["seeds"] if s["category"] == "solve"]
        assert len(sv) == 1
        put(f"r4.solverseed.{k}", sv[0]["seed"], f"round4-scores.json {k} seeds with category solve")
    # final-10% behavior table of the round-4 report (means over 20 seeds, from logs)
    rep4 = (SRC / "round4-report.md").read_text()
    beh = {}
    for l in rep4.split("**Final-10% behavior**")[1].split("Facts:")[0].splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) == 7 and c[0] and c[0][0] in "AB" and c[1][0].isdigit():
            beh[c[0].split()[0]] = dict(success=float(c[1]), key=float(c[2]), door=float(c[3]), pick=float(c[4]),
                                        length=float(c[5]), intr=float(c[6]))
    ion = [beh[k]["intr"] for k in ("B1", "B2", "B3", "B4")]
    ioff = [beh[k]["intr"] for k in ("A1b", "B7", "B6")]   # the matched tamper-off runs that solved 20/20
    put("r4.intr.on.lo", f"{min(ion):.2f}", "round4-report.md final-10% behavior, B1-B4 intrinsic return / episode")
    put("r4.intr.on.hi", f"{max(ion):.2f}", "same")
    put("r4.intr.off.lo", f"{min(ioff):.2f}", "round4-report.md final-10% behavior, A1b, B7, B6")
    put("r4.intr.off.hi", f"{max(ioff):.2f}", "same")
    put("r4.key.on.lo", f"{100 * min(beh[k]['key'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "round4-report.md, key picked up, B1-B4")
    put("r4.key.on.hi", f"{100 * max(beh[k]['key'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "same")
    put("r4.door.on.lo", f"{100 * min(beh[k]['door'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "round4-report.md, door opened, B1-B4")
    put("r4.door.on.hi", f"{100 * max(beh[k]['door'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "same")
    put("r4.len.on.lo", f"{min(beh[k]['length'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "round4-report.md, episode length, B1-B4")
    put("r4.len.on.hi", f"{max(beh[k]['length'] for k in ('B1', 'B2', 'B3', 'B4')):.0f}", "same")
    put("r4.B8.pick", f"{beh['B8']['pick']:.0f}", "round4-report.md, B8 pick-ups / episode")
    put("r4.B8.intr", f"{beh['B8']['intr']:.0f}", "round4-report.md, B8 intrinsic return / episode")
    # per-step "done" share over the final 10% of rows (Part D, exact share of steps)
    for k in ("B1", "B2", "B3", "B4"):
        v = [pd["seeds"][k][s]["done_frac_final10"] for s in pd["seeds"][k]]
        put(f"d.doneshare.{k}", f"{np.median(v):.3f}", f"part-d-results.json seeds.{k}.*.done_frac_final10, median")
    for k in ("A1b", "B7", "B5", "B6"):
        v = [pd["seeds"][k][s]["done_frac_final10"] for s in pd["seeds"][k]]
        put(f"d.doneshare.{k}", f"{np.median(v):.3f}", f"part-d-results.json seeds.{k}.*.done_frac_final10, median (no-op presses)")
    tr = J(DATA / "tamper-policy-returns.json")
    med = {}
    for k in ("B1", "B2", "B3", "B4"):
        pol = [v for kk, v in tr["policies"].items() if kk.startswith(k + "/")]
        assert len(pol) == 20
        med[k] = {m: float(np.median([q[f"mean_{m}"] for q in pol])) for m in ("disc_int", "disc_total", "mean_drive", "success")}
    for m, nm, d in (("disc_int", "disc", 3), ("disc_total", "total", 3), ("mean_drive", "drive", 3), ("success", "success", 3)):
        vals = [med[k][m] for k in med]
        put(f"tr.{nm}.lo", f"{min(vals):.{d}f}", f"tamper-policy-returns.json, per-run median over seeds of mean_{m}, minimum")
        put(f"tr.{nm}.hi", f"{max(vals):.{d}f}", f"tamper-policy-returns.json, per-run median over seeds of mean_{m}, maximum")
    put("tr.npol", len(tr["policies"]), "tamper-policy-returns.json, number of replayed checkpoints")
    put("tr.presscheck.max", f"{tr['press_share_check']['max_abs_diff']:.3f}", "tamper-policy-returns.json press_share_check.max_abs_diff")
    put("tr.cappct.lo", f"{100 * min(med[k]['disc_int'] for k in med) / D0_:.0f}", "tamper-policy-returns.json, smallest median discounted intrinsic return as % of 0.75")
    put("tr.cappct.hi", f"{100 * max(med[k]['disc_int'] for k in med) / D0_:.0f}", "same, largest")
    for k in ("B1", "B2", "B3", "B4"):
        v = [pd["seeds"][k][s]["done_frac_at"]["200000"] for s in pd["seeds"][k]]
        put(f"d.done200k.{k}", f"{np.median(v):.2f}", f"part-d-results.json seeds.{k}.*.done_frac_at[200000], median")
        e = [pd["seeds"][k][s]["entropy_at"]["200000"] for s in pd["seeds"][k]]
        put(f"d.ent200k.{k}", f"{np.median(e):.2f}", f"part-d-results.json seeds.{k}.*.entropy_at[200000], median")
    put("uniform.press", f"{1 / 7:.3f}", "1/7, uniform choice over 7 actions")
    put("uniform.press.ep", f"{640 / 7:.0f}", "640/7, uniform presses in a 640-step episode")

    # Part D (entropy, discovery, order)
    ln7 = float(np.log(7))
    put("ln7", f"{ln7:.3f}", "ln 7")
    pairs = {"B1": "A1b", "B2": "B7", "B3": "B5", "B4": "B6"}
    for on_, off_ in pairs.items():
        d = pd["D2"][f"{on_}>{off_}"]
        put(f"d2.on.{on_}", f"{d['median_on']:.3f}", f"part-d-results.json D2.{on_}>{off_}.median_on")
        put(f"d2.off.{off_}", f"{d['median_off']:.3f}", f"part-d-results.json D2.{on_}>{off_}.median_off")
    ps = {pd["D2"][k]["p"] for k in pd["D2"]}
    assert len(ps) == 1
    put("p.D2", fp(ps.pop()), "part-d-results.json D2.*.p (identical for all four pairs)")
    d2h = {preds5[f"D2-{k}"]["p_holm"] for k in ("B1", "B2", "B3", "B4")}
    put("ph.D2.max", fp(max(d2h)), "round5-scores.json predictions D2-B1..B4 p_holm, maximum")
    D1, D3 = pd["D1"], pd["D3"]
    put("d1.never", f"{D1['classes']['never found the goal']}/{D1['n']}", "part-d-results.json D1.classes")
    put("d1.lost", f"{D1['classes']['found then lost']}/{D1['n']}", "part-d-results.json D1.classes")
    put("d1.kept", f"{D1['classes']['kept solving']}/{D1['n']}", "part-d-results.json D1.classes")
    put("d1.declined", f"{D1['found_then_lost_declined']}/{D1['found_then_lost_n']}", "part-d-results.json D1")
    put("d1.declined.pct", f"{100 * D1['found_then_lost_declined'] / D1['found_then_lost_n']:.0f}", "same, percent")
    put("d1.firstgoal.median", comma(D1["first_goal_median"]), "part-d-results.json D1.first_goal_median")
    put("d1.firstgoal.max", comma(D1["first_goal_max"]), "part-d-results.json D1.first_goal_max")
    put("d3.rise", f"{D3['rise_first']}/{D3['seeds_with_both']}", "part-d-results.json D3")
    put("d3.n", D3["seeds_with_both"], "part-d-results.json D3.seeds_with_both")
    put("d3.norise", D3["no_rise"], "part-d-results.json D3.no_rise")
    put("d3.nodecline", D3["no_decline"], "part-d-results.json D3.no_decline")
    put("p.D3", fp(D3["p_binom"]), "part-d-results.json D3.p_binom")

    # ---------------------------------------------------------------- round 5: Parts A, B, C
    for k in ("A1", "A2", "B9", "B10", "B11", "C1", "C2", "C3", "C4", "C5", "C6", "r4-B1", "r4-B2", "r4-B3", "r4-A1b"):
        d = R5[k]
        kk = k.replace("r4-", "r4")
        s = cat(d)["solve"]
        put(f"r5.solve.{kk}", f"{s}/{d['n']}", f"round5-scores.json runs.{k}.categories.solve")
        put(f"r5.ci.{kk}", ci(s, d["n"]), f"Clopper-Pearson 95% of runs.{k} solve")
        put(f"r5.auc.{kk}", f"{d['auc_mean']:.3f}", f"round5-scores.json runs.{k}.auc_mean")
        put(f"r5.farm.{kk}", f"{cat(d)['cycle-farm']}/{d['n']}", f"round5-scores.json runs.{k}.categories.cycle-farm")
        put(f"r5.tamperers.{kk}", f"{d['tamperers']}/{d['n']}", f"round5-scores.json runs.{k}.tamperers")
    b13 = [s["auc"] for s in R5["r4-B1"]["seeds"]] + [s["auc"] for s in R5["r4-B3"]["seeds"]]
    put("r5.auc.B1B3", f"{np.mean(b13):.3f}", "round5-scores.json r4-B1 and r4-B3 per-seed auc, pooled mean")
    put("r5.solve.B1B3", f"{cat(R5['r4-B1'])['solve'] + cat(R5['r4-B3'])['solve']}/40", "round5-scores.json r4-B1 + r4-B3")
    for t in ("A-P1", "A-P1m", "A-P2", "A-P2m", "A-P3", "A-P3m", "B-JTp", "B-JTs", "B-F-B9-vsB1", "B-F-B9-vsA1b",
              "B-F-B10-vsB1", "B-F-B10-vsA1b", "B-F-B11-vsB1", "B-F-B11-vsA1b", "C-P1", "C-P2", "C-P3", "C-P4"):
        put(f"p.{t}", fp(preds5[t]["p"]), f"round5-scores.json predictions[{t}].p")
        if preds5[t].get("p_holm") is not None:
            put(f"ph.{t}", fp(preds5[t]["p_holm"]), f"round5-scores.json predictions[{t}].p_holm")
    # B-L level predictions (registered on per-episode medians; quoted only next to their registration)
    pre5 = (SRC / "round5-preregistration.md").read_text()
    for t in ("B-L-B9-presses", "B-L-B9-tamperers", "B-L-B9-solves", "B-L-B10-presses", "B-L-B10-tamperers", "B-L-B10-solves",
              "B-L-B11-presses", "B-L-B11-tamperers", "B-L-B11-solves"):
        m = re.search(r"^\| %s \| (\S+) \((\d+)-(\d+)\) \|" % re.escape(t), pre5, re.M)
        assert m.group(1) == preds5[t]["expected"].split()[0], t
        put(f"exp.{t}", m.group(1), f"round5-preregistration.md, {t} expected")
        put(f"rng.{t}", f"{m.group(2)}--{m.group(3)}", f"round5-preregistration.md, {t} range")
        put(f"obs.{t}", preds5[t]["observed"], f"round5-scores.json predictions[{t}].observed")
    # presses per step over the final 10% of rows (descriptive, from run-series.json)
    for k in ("B1", "B9", "B10", "B11", "A1b"):
        v = np.array([s["presses_per_step"] for s in rs["presses"][k].values()])
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        put(f"pps.{k}", f"{med:.3f}", f"run-series.json presses.{k} presses_per_step, median")
        put(f"pps.iqr.{k}", f"[{q1:.3f}, {q3:.3f}]", f"run-series.json presses.{k}, interquartile range")
        L = np.array([s["mean_len_final10"] for s in rs["presses"][k].values()])
        put(f"len.{k}", f"{np.median(L):.0f}", f"run-series.json presses.{k} mean_len_final10, median")
    # Step 0 (exact optimum on the small grid, explore need omitted)
    for g, gk in (("1/160", "160"), ("1/40", "40")):
        grid = s0[g]["grid"]
        lt, nt = s0[g]["largest_c_still_tampers"], s0[g]["smallest_c_no_tamper"]
        put(f"s0.{gk}.tamper", f"{lt:.4f}".rstrip("0"), f"step0-tamper-cost.json {g}.largest_c_still_tampers")
        put(f"s0.{gk}.notamper", f"{nt:.4f}".rstrip("0"), f"step0-tamper-cost.json {g}.smallest_c_no_tamper")
        v0 = next(x["V_start"] for x in grid if x["c"] == 0.0)
        vinf = next(x["V_start"] for x in grid if x["c"] == 1.0)
        put(f"s0.{gk}.adv", f"{v0 - vinf:.3f}", f"step0-tamper-cost.json {g}: V_start(c=0) - V_start(c=1)")
        assert all(x["outcome"] == "reaches goal" for x in grid)
    # Part C
    for k in ("C1", "C2", "C3", "C6"):
        fs = [s["first_solved"] for s in R5[k]["seeds"]]
        put(f"r5.fs.{k}", kfmt(np.median(fs)), f"round5-scores.json runs.{k}.seeds.first_solved, median")
    for k in ("C1", "C2", "C3", "C4", "C5", "C6"):
        v = np.array([s["peak_key_pickups"] for s in rs["keycorridor_pickups"][k].values()])
        put(f"kc.peak.{k}", f"{np.median(v):.1f}", f"run-series.json keycorridor_pickups.{k} peak, median")
        put(f"kc.peakmax.{k}", f"{v.max():.1f}", f"run-series.json keycorridor_pickups.{k} peak, maximum")
    fin = [R5[k]["pickups_median"] for k in ("C1", "C2", "C3", "C4")]
    put("kc.final.lo", f"{min(fin):.1f}", "round5-scores.json C1-C4 pickups_median, minimum")
    put("kc.final.hi", f"{max(fin):.1f}", "round5-scores.json C1-C4 pickups_median, maximum")
    put("kc.C5.pick", f"{R5['C5']['pickups_median']:.2f}", "round5-scores.json runs.C5.pickups_median")
    over = [(k, s) for k in ("C1", "C2", "C3", "C4") for s in R5[k]["seeds"] if s["repeat_over_5"]]
    put("kc.overrepeat", f"{len(over)}/80", "round5-scores.json C1-C4 seeds with repeat_over_5")
    put("kc.final.max", f"{max(s['pickups'] for k in ('C1', 'C2', 'C3', 'C4') for s in R5[k]['seeds']):.2f}",
        "round5-scores.json C1-C4 per-seed final key pick-ups, maximum")
    rep5 = (SRC / "round5-report.md").read_text()
    m = re.search(r"C5's final policy entropy has a median of ([0-9.]+)", rep5)
    put("kc.C5.entropy", m.group(1), "round5-report.md, Part C exploratory paragraph")
    amd = (SRC / "round5-amendment-20261027T113334Z.md").read_text()
    m = re.search(r"\| C-P1 \| farming rises C1 < C2 < C3 \| farmers C1 (\S+) \(([^)]+)\), C2 (\S+) \(([^)]+)\), C3 (\S+) \(([^)]+)\)", amd)
    put("exp.C3.farm", m.group(5), "round5 amendment, C-P1 expectation for C3")
    put("exp.C3.range", m.group(6).replace("-", "--"), "round5 amendment, C-P1 range for C3")
    put("exp.C2.farm", m.group(3), "round5 amendment, C-P1 expectation for C2")
    m = re.search(r"\| C-P3 \| C5 solves less often than C1 \| C5 (\S+) \(([^)]+)\)", amd)
    put("exp.C5.solve", m.group(1), "round5 amendment, C-P3 expectation for C5")
    # Part A-2 normalization-off presses (uniform rate)
    put("r5.A2.presses.ep", f"{R5['A2']['presses_median']:.0f}", "round5-scores.json runs.A2.presses_median")
    put("r5.A2.pick", f"{R5['A2']['pickups_median']:.2f}", "round5-scores.json runs.A2.pickups_median")

    put("holm.r4", r4["holm_m"], "round4-scores.json holm_m")
    put("holm.r5", sum(1 for x in r5["predictions"] if x.get("holm_eligible")), "round5-scores.json predictions holm_eligible")

    # ---------------------------------------------------------------- C4: urgency and fair exploration (round 4)
    for k in ("A1a", "A1b", "A1c"):
        put(f"r4.fs.{k}", comma(R4[k]["medians"]["first_solved"]), f"round4-scores.json runs.{k}.medians.first_solved")
        put(f"r4.sl.{k}", f"{R4[k]['medians']['solved_len']:.1f}", f"round4-scores.json runs.{k}.medians.solved_len")
    for k in ("A2a", "A2b", "A2c"):
        for g, gk in (("DoorKey-8x8", "8"), ("DoorKey-16x16", "16")):
            v = [s["curve"][g] for s in R4[k]["seeds"]]
            put(f"r4.curve{gk}.{k}", f"{np.mean(v):.3f}", f"round4-scores.json runs.{k}.seeds.curve[{g}], mean")
        put(f"r4.solve16.{k}", f"{R4[k]['solve16']}/{R4[k]['n']}", f"round4-scores.json runs.{k}.solve16")
    put("a2.coef.640", f"{a2m['coef']['explore_1/640']['value']:.3f}", "a2-matching.json coef explore_1/640")
    put("a2.coef.160", f"{a2m['coef']['explore_1/160']['value']:.3f}", "a2-matching.json coef explore_1/160")

    # ---------------------------------------------------------------- C5: farming (rounds 2-5)
    R3 = r3["round3"]
    for k in R3:
        put(f"r3.farm.{k}", f"{R3[k]['counts']['cycle-farm']}/{R3[k]['n']}", f"round3-scores.json round3.{k}.counts.cycle-farm")
        put(f"r3.solve.{k}", f"{R3[k]['counts']['solve']}/{R3[k]['n']}", f"round3-scores.json round3.{k}.counts.solve")
    put("r3.normon.total", f"{sum(R3[k]['counts']['cycle-farm'] for k in ('R3', 'R4', 'R5'))}/60", "round3-scores.json R3+R4+R5 cycle-farm")
    put("r3.normoff.total", f"{sum(R3[k]['counts']['cycle-farm'] for k in ('R6', 'R7', 'R8'))}/60", "round3-scores.json R6+R7+R8 cycle-farm")
    for t, key in (("R1 < R4 (Fisher, one-sided)", "R1<R4"), ("R2 > R4 (Fisher, one-sided)", "R2>R4"),
                   ("R8 > R6 (Fisher, one-sided)", "R8>R6"), ("R9 < R4 (Fisher, one-sided)", "R9<R4")):
        put(f"p.{key}", fp(r3["tests"][t]), f"round3-scores.json tests[{t}]")
    pr3 = {x["prediction"]: x for x in r3["prediction_rows"]}
    for k in ("R7", "R8", "R9"):
        x = pr3[f"{k} cycle-farm"]
        put(f"exp.{k}.range", f"{x['range'][0]}--{x['range'][1]}", f"round3-scores.json prediction_rows[{k} cycle-farm].range")
    ex = r3["exploratory_rescore"]
    name2 = {"N1": "N1: anchor replicate, growth 1/40, seeds 10-19", "N2": "N2: growth 1/40 at gamma 0.95", "N3": "N3: growth 1/80",
             "N4": "N4: growth 1/80, coef 1.29 (matched to anchor)", "N5": "N5: growth 1/40, coef 0.5", "N6": "N6: growth 1/20"}
    for k, nm in name2.items():
        put(f"r2.farm.{k}", f"{r2[k]['farmers']}/{r2[k]['n']}", f"round2-prediction-results.json {k}.farmers (round-2 rule)")
        put(f"r2.rescore.{k}", f"{ex[nm]['counts']['cycle-farm']}/{ex[nm]['n']}", f"round3-scores.json exploratory_rescore[{nm}]")
        put(f"r2.E.{k}", f"{r2[k]['E']}", f"round2-prediction-results.json {k}.E")
        put(f"r2.range.{k}", f"{r2[k]['predicted'][0]}--{r2[k]['predicted'][1]}", f"round2-prediction-results.json {k}.predicted")
    put("r2.farm.payonce", f"{r2['Control: pay each event once']['farmers']}/10", "round2-prediction-results.json pay-once control")
    for t in ("N2 < N1", "N5 < N4", "N6 > N3"):
        put(f"p.{t.replace(' ', '')}", fp(r2["fisher"][t]["p"]), f"round2-prediction-results.json fisher[{t}].p")
    put("r2.slope", f"{r2['logistic']['slope']:.2f}", "round2-prediction-results.json logistic.slope")
    put("p.r2logistic", fp(r2["logistic"]["p_one_sided"]), "round2-prediction-results.json logistic.p_one_sided")
    # N6 replay: farmers' behaviour
    farm_seeds = [s for s, v in rep["seeds"].items() if v["success"] < 0.5]
    ri = [rep["seeds"][s]["r_int"] for s in farm_seeds]
    put("n6.rint.lo", neg(f"{min(ri):.2f}"), "round2-replay-n6.json seeds (success < 0.5) r_int, minimum")
    put("n6.rint.hi", neg(f"{max(ri):.2f}"), "round2-replay-n6.json seeds (success < 0.5) r_int, maximum")
    pk = [rep["seeds"][s]["pickups"] for s in farm_seeds]
    put("n6.pick.lo", f"{min(pk):.0f}", "round2-replay-n6.json farmer pickups per episode, minimum")
    put("n6.pick.hi", f"{max(pk):.0f}", "round2-replay-n6.json farmer pickups per episode, maximum")
    sh = [rep["seeds"][s]["action_freq"]["pickup"] + rep["seeds"][s]["action_freq"]["drop"] for s in farm_seeds]
    put("n6.pdshare.lo", f"{100 * min(sh):.0f}", "round2-replay-n6.json farmer action_freq pickup+drop, minimum (%)")
    put("n6.pdshare.hi", f"{100 * max(sh):.0f}", "round2-replay-n6.json farmer action_freq pickup+drop, maximum (%)")
    put("n6.nfarm", len(farm_seeds), "round2-replay-n6.json seeds with success < 0.5")
    for j, nm in ((0, "explore"), (1, "grasp"), (2, "open")):
        v = [rep["seeds"][s]["mean_need"][j] for s in farm_seeds]
        put(f"n6.need.{nm}.lo", f"{min(v):.2f}", f"round2-replay-n6.json farmer mean_need[{nm}], minimum")
        put(f"n6.need.{nm}.hi", f"{max(v):.2f}", f"round2-replay-n6.json farmer mean_need[{nm}], maximum")
        lo_, hi_ = f"{min(v):.2f}", f"{max(v):.2f}"
        put(f"n6.need.{nm}", lo_ if lo_ == hi_ else f"{lo_}--{hi_}", f"round2-replay-n6.json farmer mean_need[{nm}], range")
    # hypothesis-level accounting (grouping defined in make_tables.py, which must run first)
    acc = J(DATA / "tables-summary.json")["accounting"]
    put("acct.groups", acc["groups"], "tables-summary.json (make_tables.py grouping of consolidated rows)")
    put("acct.supported", acc["supported"], "tables-summary.json")
    put("acct.notsupported", acc["not_supported"], "tables-summary.json")
    # race account (round 3, Step 1)
    put("race.P1.undet", f"{race['P1']['undetermined']}/{race['P1']['n']}" if "undetermined" in race["P1"] else "?", "race-results.json P1")
    put("race.P2", f"{race['P2']['k']}/{race['P2']['n']}", "race-results.json P2")
    put("p.race.P2", fp(race["P2"]["p_binom_gt_half"]), "race-results.json P2.p_binom_gt_half")

    # ---------------------------------------------------------------- theory: value iteration (rounds 3-5)
    vi_main = [x for x in vi3 if x["bin"] == "g"]
    reach = sorted({x["growth"] for x in vi_main if x["outcome"] == "reaches goal"}, key=lambda s: -eval(s))
    cyc = sorted({x["growth"] for x in vi_main if x["outcome"] != "reaches goal"}, key=lambda s: -eval(s))
    put("vi.maxreach", max(reach, key=lambda s: eval(s)), "value-iteration-results.json: largest growth that reaches the goal")
    put("vi.cycles", ", ".join(cyc), "value-iteration-results.json: growth values whose greedy rollout cycles")
    put("vi.steps", min(x["steps"] for x in vi_main if x["outcome"] == "reaches goal"), "value-iteration-results.json shortest optimal route")
    for x in b0:
        if x["bin"] != "g":
            continue
        gk = x["growth"].split("/")[1]
        put(f"b0.{gk}.tampers", x["tampers"], f"b0-value-iteration.json {x['growth']} tampers")
        put(f"b0.{gk}.at", ", ".join(str(t) for t in x["tamper_steps"]), f"b0-value-iteration.json {x['growth']} tamper_steps")
        put(f"b0.{gk}.steps", x["steps"], f"b0-value-iteration.json {x['growth']} steps")

    # ---------------------------------------------------------------- theory: post-hoc bound check
    dk, kc = bc["envs"]["MiniGrid-DoorKey-8x8-v0"], bc["envs"]["MiniGrid-KeyCorridorS3R1-v0"]
    put("bc.layouts", bc["layouts"], "bound-check.json layouts")
    for e, ek in ((dk, "dk"), (kc, "kc")):
        for s in ("min", "median", "max"):
            put(f"bc.{ek}.len.{s}", f"{e['shortest_len'][s]:.0f}", f"bound-check.json shortest_len.{s}")
    g20 = dk["growth"]["1/20"]
    put("bc.dk20.short.le", g20["shortest_no_tamper"]["layouts_discounted_at_or_below_D0"], "bound-check.json DoorKey 1/20 shortest_no_tamper")
    put("bc.dk20.short.le.u", g20["shortest_no_tamper"]["layouts_undiscounted_at_or_below_D0"], "same, undiscounted")
    put("bc.dk20.short.min", f"{g20['shortest_no_tamper']['discounted_min']:.3f}", "same, discounted_min")
    put("bc.dk20.tamper.le", g20["tamper_once_then_shortest"]["layouts_discounted_at_or_below_D0"], "bound-check.json DoorKey 1/20 tamper_once_then_shortest")
    put("bc.dk20.rich.min", f"{g20['rich_no_tamper_family']['discounted_min']:.3f}", "bound-check.json DoorKey 1/20 rich_no_tamper_family.discounted_min")
    put("bc.dk20.rich.umin", f"{g20['rich_no_tamper_family']['undiscounted_min']:.3f}", "same, undiscounted_min")
    put("bc.dk20.rich.regrab", g20["rich_no_tamper_family"]["best_variant_counts_discounted"]["regrab"], "same, best variant counts (regrab)")
    simple_min = min(min(v["shortest_no_tamper"]["discounted_min"], v["tamper_once_then_shortest"]["discounted_min"])
                     for g, v in dk["growth"].items() if g != "1/20")
    put("bc.dk.simplemin.not20", f"{simple_min:.3f}", "bound-check.json DoorKey growth != 1/20, simple families, smallest discounted_min")
    tam = [dk["growth"]["1/160"]["rich_tamper_family"]["discounted_min"], dk["growth"]["1/40"]["rich_tamper_family"]["discounted_min"],
           kc["growth"]["1/160"]["rich_tamper_family"]["discounted_min"]]
    put("bc.tamperfam.min", f"{min(tam):.3f}", "bound-check.json rich_tamper_family discounted_min, tamper-tested rates, minimum")
    allmins = [v[f]["discounted_min"] for e in (dk, kc) for g, v in e["growth"].items() for f in ("rich_no_tamper_family",)]
    put("bc.rich.min.all", f"{min(allmins):.3f}", "bound-check.json rich_no_tamper_family discounted_min over all settings")
    # check (b): learned farming policies
    put("bs.nfarm", len(bs["farming_policy_seeds"]), "bound-summary.json farming_policy_seeds")
    put("bs.mean", f"{bs['farmers_mean_discounted']:.3f}".replace("-", "$-$"), "bound-summary.json farmers_mean_discounted")
    put("bs.maxns", f"{bs['max_discounted_non_solving']:.3f}".replace("-", "$-$"), "bound-summary.json max_discounted_non_solving")
    put("bs.maxns.u", f"{bs['max_undiscounted_non_solving']:.3f}".replace("-", "$-$"), "bound-summary.json max_undiscounted_non_solving")
    put("bs.nns", comma(bs["non_solving_episodes"]), "bound-summary.json non_solving_episodes")
    put("bs.beat", bs["layouts_where_any_farmer_beats_best_solving"], "bound-summary.json layouts_where_any_farmer_beats_best_solving")
    put("bs.best.min", f"{bs['best_solving_discounted']['min']:.3f}", "bound-summary.json best_solving_discounted.min")
    put("bs.best.median", f"{bs['best_solving_discounted']['median']:.3f}", "bound-summary.json best_solving_discounted.median")
    put("bs.solveeps", bs["solving_episodes_by_farming_seeds"], "bound-summary.json solving_episodes_by_farming_seeds")
    put("bs.solverseed.rate", f"{bs['learned_policies'][bs['solver_seeds'][0]]['success_rate']:.3f}", "bound-summary.json solver seed success_rate")
    put("bs.n6seed6.rate", f"{bs['learned_policies']['6']['success_rate']:.2f}", "bound-summary.json learned_policies.6.success_rate")

    # ---------------------------------------------------------------- compute and software
    txt = (DATA / "orx-runs.txt").read_text().splitlines()[2:]
    def secs(s):
        h = re.search(r"(\d+)h", s); m_ = re.search(r"(\d+)m", s); s_ = re.search(r"(\d+)s", s)
        return (int(h.group(1)) * 3600 if h else 0) + (int(m_.group(1)) * 60 if m_ else 0) + (int(s_.group(1)) if s_ else 0)
    def rnd(name):
        if name.startswith("R5-"): return 5
        if re.match(r"^(A1[abc]|A2[abc]|B[1-8]):", name): return 4
        if re.match(r"^R(10|[1-9]):", name): return 3
        if re.match(r"^N[1-6]:", name) or name.startswith("Control: pay each event once"): return 2
        return 1
    tot = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}; cnt = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for l in txt:
        c = re.split(r"\s{2,}", l.strip())
        if len(c) < 6 or c[1] != "done":
            continue
        r = rnd(c[2]); tot[r] += secs(c[4]); cnt[r] += 1
    put("compute.runs.r25", sum(cnt[r] for r in (2, 3, 4, 5)), "orx-runs.txt, rounds 2-5 runs")
    put("compute.hours.r25", f"{sum(tot[r] for r in (2, 3, 4, 5)) / 3600:.1f}", "orx-runs.txt, rounds 2-5 summed wall-clock")
    put("compute.runs.r1", cnt[1], "orx-runs.txt, round-1 runs")
    put("compute.hours.r1", f"{tot[1] / 3600:.1f}", "orx-runs.txt, round-1 summed wall-clock")
    import hashlib
    for key, fn in (("r3", "round3-preregistration.md"), ("r4", "round4-preregistration.md"),
                    ("r4a", "round4-amendment-20261026T192733Z.md"), ("r5", "round5-preregistration.md"),
                    ("r5a", "round5-amendment-20261027T113334Z.md")):
        put(f"hash.{key}", hashlib.sha256((SRC / fn).read_bytes()).hexdigest(), f"sha256 of paper/data/sources/{fn}")
    for r in ("3", "4", "5"):
        h, ts = (SRC / f"round{r}-preregistration.sha256").read_text().split("\n")[:2]
        assert h.split()[0] == V[f"hash.r{r}"][0], f"round {r}: snapshot hash differs from the locked record"
        put(f"lock.r{r}", ts.strip().replace("T", " ").replace("Z", ""), f"round{r}-preregistration.sha256 (lock time, UTC)")
    lock = (ROOT / "uv.lock").read_text()
    for name in ("torch", "gymnasium", "minigrid", "numpy"):
        m = re.search(r'\[\[package\]\]\nname = "%s"\nversion = "([^"]+)"' % name, lock)
        put(f"ver.{name}", m.group(1), f"uv.lock {name}")

    # ---------------------------------------------------------------- "k of n" variants of every count
    for k, (txt, src) in list(V.items()):
        if re.fullmatch(r"\d+/\d+", txt):
            put(k + ".of", txt.replace("/", " of "), src + " (written as 'k of n')")

    # ---------------------------------------------------------------- write
    out_tex = ["% Generated by paper/scripts/make_numbers.py from paper/data. Do not edit by hand.",
               r"\makeatletter"]
    for k, (t, s) in V.items():
        out_tex.append(r"\@namedef{val@" + k + "}{" + t + "}")
    out_tex.append(r"\makeatother")
    return "\n".join(out_tex) + "\n", json.dumps({k: dict(text=t, source=s) for k, (t, s) in V.items()}, indent=1)


if __name__ == "__main__":
    tex, js = main()
    if "--stdout" in sys.argv:
        print(tex)
    else:
        (P / "numbers.tex").write_text(tex)
        (DATA / "numbers.json").write_text(js)
        print(f"wrote {len(V)} values to paper/numbers.tex and paper/data/numbers.json")
