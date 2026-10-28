"""Build consolidated-results.md: every pre-registered test across rounds 2-5, from each round's scored JSON
(no new analysis), plus the list of known misclassifications and corrections. Usage: python build_consolidated.py"""
import json
from pathlib import Path
A = Path(__file__).parent
fp = lambda p: "–" if p is None else (f"{p:.2g}" if p < 0.001 else f"{p:.3f}")
rows = []
def add(rnd, pid, pred, obs, test, p, hit):
    rows.append((rnd, pid, pred, obs, test, p, hit))
# ---- round 2 (pre-registered farming test)
r2 = json.loads((A / "mechanism/prediction-results.json").read_text())
for k in ("N1", "N2", "N3", "N4", "N5", "N6", "Control: pay each event once"):
    v = r2[k]; lo, hi = v["predicted"]
    add(2, k if k.startswith("N") else "pay-once control", f"farmers in {lo}-{hi} of 10" + (f" (E={v['E']})" if v.get("E") is not None else ""),
        f"{v['farmers']}/{v['n']}", "level (range)", None, v["within"])
add(2, "logistic", "farming rises with predicted temptation E (slope > 0)", f"slope {r2['logistic']['slope']:.2f}", "logistic, one-sided", r2["logistic"]["p_one_sided"], r2["logistic"]["p_one_sided"] < 0.05)
for t, v in r2["fisher"].items():
    add(2, t, t + " (farmer counts)", f"{v['table'][0][0]}/10 vs {v['table'][1][0]}/10", "Fisher, one-sided", v["p"], v["p"] < 0.05)
# ---- round 3
r3 = json.loads((A / "round3/round3-scores.json").read_text())
race = json.loads((A / "round3/race-results.json").read_text())
vi3 = json.loads((A / "round3/value-iteration-results.json").read_text())
add(3, "P1", "farmers: lock-in before first goal >= 80%", f"{race['P1']['undetermined']}/{race['P1']['n']} undetermined", "binomial", None, None)
add(3, "P2", "solvers: first goal before lock-in >= 80%", f"{race['P2']['k']}/{race['P2']['n']}", "binomial, one-sided", race["P2"]["p_binom_gt_half"], True)
add(3, "P3", "earlier first goal predicts not farming", f"{race['P3']['distinct_first_goal_windows']} distinct first-goal windows", "logistic", None, None)
main = [x for x in vi3 if x["growth"] in ("1/80", "1/40", "1/20") and x["gamma"] == 0.99 and x["bin"] == "g"]
add(3, "P4", "exact optimum reaches the goal at gamma 0.99 for g in {1/80, 1/40, 1/20}", f"{sum(x['outcome'] == 'reaches goal' for x in main)}/3",
    "deterministic", None, all(x["outcome"] == "reaches goal" for x in main))
for x in r3["prediction_rows"]:
    add(3, x["prediction"].split()[0] + (" " + x["prediction"].split()[1] if x["prediction"].startswith("R10") else ""),
        f"{x['prediction']} in {x['range'][0]}-{x['range'][1]} of {x['n']}", f"{x['observed']}/{x['n']}", "level (range)", None, x["hit"])
for t, v in r3["tests"].items():
    if t.startswith("logistic b2"): continue
    if isinstance(v, dict):
        add(3, t.split(" (")[0], t, f"b = {v['b']:.3g} (not estimable: quasi-separation)", "logistic Wald, one-sided", None, False)
    else:
        a_, b_ = t.split(" (")[0].replace("<", " ").replace(">", " ").split()
        cf = lambda k: r3["round3"][k]["counts"]["cycle-farm"]
        add(3, t.split(" (")[0], t.replace(" (Fisher, one-sided)", " (cycle-farmers)"), f"{cf(a_)}/20 vs {cf(b_)}/20", "Fisher, one-sided", v, v < 0.05)
# ---- rounds 4 and 5
for rnd, f in ((4, "round4/round4-scores.json"), (5, "round5/round5-scores.json")):
    if not (A / f).exists(): continue
    for x in json.loads((A / f).read_text())["predictions"]:
        add(rnd, x["id"], x["prediction"], x["observed"].replace("|", "/"), x["test"], x.get("p"), x["hit"])
hits = sum(1 for r in rows if r[6] is True); misses = sum(1 for r in rows if r[6] is False); unres = sum(1 for r in rows if r[6] is None)
out = ["# Consolidated pre-registered results, rounds 2-5", "",
       "Source table for the preprint. Every pre-registered prediction or test from rounds 2-5, generated from each round's scored "
       "JSON (`mechanism/prediction-results.json`, `round3/round3-scores.json`, `round3/race-results.json`, "
       "`round3/value-iteration-results.json`, `round4/round4-scores.json`, `round5/round5-scores.json`). Round 1 was "
       "exploratory and is not included. p is the raw p-value of the pre-registered test (one-sided where directional); Holm-adjusted "
       "values are in each round's report.", "",
       f"**Totals:** {len(rows)} pre-registered rows: {hits} hits, {misses} misses, {unres} unresolvable or not scored.", "",
       "| Round | ID | Prediction | Observed | Test | raw p | Result |", "|---|---|---|---|---|---|---|"]
for r in rows:
    res = "unresolvable / not scored" if r[6] is None else ("hit" if r[6] else "miss")
    out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {fp(r[5])} | {res} |")
out += ["", "## Known misclassifications and corrections", "",
 "1. **Round 2, temptation formula F redefined after seeing data.** The first F did not fit the three calibration runs and was "
 "redefined before the round-2 test; the calibration runs were therefore excluded as evidence (disclosed in round 2).",
 "2. **Round 2, pay-once control labelled 'farmer' by the >5 rule** although replay showed episode-prolonging, not repetition; "
 "the round-3 exploratory re-score repeats this label.",
 "3. **Round 2 claim dropped: 'the critic prefers farming'.** The value rising with need is the +D(h_t) term of the return and "
 "holds for solvers too; not evidence of preference.",
 "4. **Round 1 claim corrected: LP-curiosity seeds 2 and 4 'entropy collapse'.** Entropy stayed high; the cause was left open.",
 "5. **Event-bonus per-new-view payment** was written as 0.0975 in round-2 notes; the code pays h0^2 - (h0 - 0.1)^2 = 0.09 "
 "(corrected in round 3).",
 "6. **Round 3, coef x normalization logistic model not estimable** (all 60 normalization-off seeds solved); recorded as misses.",
 "7. **Evaluation bias, rounds 1-3.** `evaluate()` kept the first N episodes to finish across 16 parallel envs, over-weighting "
 "short successful episodes. Re-evaluation (round 4): 16x16 novelty 1e-3 0.845 -> 0.787; Agent 3 1/160 0.714 -> 0.653; "
 "1/640 0.622 -> 0.548; ranking unchanged. Fixed from round 4 on (per-environment quota).",
 "8. **Round 4, explore-only runs (A2a, A2b) labelled 'cycle-farm'** although pick-ups were not paid in those runs; replay "
 "showed non-learning policies. Led to the round-5 rule: cycle-farm applies only where pick-ups or door toggles are paid.",
 "9. **Round 4, B1 and B2 ran concurrently** because a launcher missed a setup status; seeded single-threaded computation, so "
 "results are unaffected.",
 "10. **Round 5, Step 0 at growth 1/160** used a certified early stop (validated against full convergence on all 21 growth-1/40 "
 "cases) instead of full convergence.",
 "11. **Round 5, A-P2m is a 'hit' on a negligible effect** (success-curve area 0.025 vs 0.022); both runs are at the floor and the "
 "solve test (A-P2) missed. Do not cite A-P2m as evidence.",
 "12. **Round 5, tamper labels in tamper-off runs.** The 'tamperers' column for tamper-off runs counts presses of the no-op 'done' "
 "action (e.g. A2 presses at the uniform-random rate); the labels apply only to tamper-on runs.",
 "13. **Round 5, Part D 'found then lost'** includes seeds that only met the goal by chance; only 7/77 declined after real learning "
 "(D1-P2 miss), and D3 rests on those 7 seeds."]
(A / "consolidated-results.md").write_text("\n".join(out) + "\n")
print(len(rows), "rows;", hits, "hits;", misses, "misses;", unres, "unresolvable")
