"""Pull every number the paper cites out of the scored JSON files (no new analysis) into paper/data/claims.json.
Sources: <artifacts>/three-agents/{consolidated-results.md, mechanism/*.json, round3/*.json, round4/*.json, round5/*.json}.
Usage: python paper/scripts/extract_claims.py <artifacts three-agents dir> paper/data/claims.json"""
import json, sys
from pathlib import Path
A, out = Path(sys.argv[1]), Path(sys.argv[2])
J = lambda p: json.loads((A / p).read_text())
r2, r3, r4, r5 = J("mechanism/prediction-results.json"), J("round3/round3-scores.json"), J("round4/round4-scores.json"), J("round5/round5-scores.json")
pd, s0, vi3, b0 = J("round5/part-d-results.json"), J("round5/step0-tamper-cost.json"), J("round3/value-iteration-results.json"), J("round4/b0-value-iteration.json")
n6 = J("mechanism/replay-n6.json")
P4 = {x["id"]: x for x in r4["predictions"]}; P5 = {x["id"]: x for x in r5["predictions"]}
S4, S5 = r4["runs"], r5["runs"]
sol4 = lambda k: S4[k]["categories"]["solve"]; sol5 = lambda k: S5[k]["categories"]["solve"]
c = {}
# C1 wireheading
c["C1"] = dict(
    doorkey_round4=dict(tamper_on={k: sol4(k) for k in ("B1", "B2", "B3", "B4")}, tamper_off={k: sol4(k) for k in ("A1b", "B7", "B5", "B6")},
                        tests={k: dict(observed=P4[k]["observed"], p=P4[k]["p"], p_holm=P4[k].get("p_holm")) for k in ("PB2-B1", "PB2-B2", "PB2-B3", "PB2-B4")},
                        runs={k: S4[k]["run"] for k in ("B1", "B2", "B3", "B4", "A1b", "B7", "B5", "B6")}),
    doorkey_round5_B9=dict(solve=sol5("B9"), run=S5["B9"]["run"], test=dict(observed=P5["B-F-B9-vsA1b"]["observed"], p=P5["B-F-B9-vsA1b"]["p"])),
    keycorridor_C5=dict(solve=sol5("C5"), C1=sol5("C1"), C6=sol5("C6"), runs={k: S5[k]["run"] for k in ("C5", "C1", "C6")},
                        tests={k: dict(observed=P5[k]["observed"], p=P5[k]["p"], p_holm=P5[k].get("p_holm")) for k in ("C-P3", "C-P4")}),
    entropy_D2={k: dict(median_on=v["median_on"], median_off=v["median_off"], p=v["p"]) for k, v in pd["D2"].items()},
    uniform_entropy_ln7=1.9459101090932196)
# C2 self-fillable signal worse than none
c["C2"] = dict(A1_solve=sol5("A1"), A1_auc=S5["A1"]["auc_mean"], B1_solve=sol5("r4-B1"), B1_auc=S5["r4-B1"]["auc_mean"],
               B1B3_solve=sol5("r4-B1") + sol5("r4-B3"), A2_solve=sol5("A2"), A2_auc=S5["A2"]["auc_mean"], B2_auc=S5["r4-B2"]["auc_mean"],
               tests={k: dict(observed=P5[k]["observed"], p=P5[k]["p"], p_holm=P5[k].get("p_holm"), hit=P5[k]["hit"]) for k in ("A-P1", "A-P1m", "A-P2", "A-P2m", "A-P3", "A-P3m")},
               runs={k: S5[k]["run"] for k in ("A1", "A2")})
# C3 cost restores task
c["C3"] = dict(solve={k: sol5(k) for k in ("r4-B1", "B9", "B10", "B11", "r4-A1b")}, auc={k: S5[k]["auc_mean"] for k in ("r4-B1", "B9", "B10", "B11", "r4-A1b")},
               presses_per_episode_median={k: S5[k]["presses_median"] for k in ("r4-B1", "B9", "B10", "B11")},
               tamperers={k: S5[k]["tamperers"] for k in ("B9", "B10", "B11")},
               tests={k: dict(observed=P5[k]["observed"], p=P5[k]["p"], p_holm=P5[k].get("p_holm"), hit=P5[k]["hit"]) for k in P5 if k.startswith("B-")},
               step0={g: dict(largest_c_still_tampers=v["largest_c_still_tampers"], smallest_c_no_tamper=v["smallest_c_no_tamper"], reaches_goal_at_every_c=v["reaches_goal_at_every_c"]) for g, v in s0.items()},
               runs={k: S5[k]["run"] for k in ("B9", "B10", "B11")})
# C4 satiation no exploration benefit (round 4 A1 urgency, A2 explore-only vs novelty)
c["C4"] = dict(tests={k: dict(observed=P4[k]["observed"], p=P4[k]["p"], p_holm=P4[k].get("p_holm"), hit=P4[k]["hit"]) for k in P4 if k.startswith(("A1-", "A2-"))},
               curve_means={k: {g: S4[k]["mean curve " + g] for g in ("DoorKey-8x8", "DoorKey-16x16")} for k in ("A2a", "A2b", "A2c")},
               solves_8x8={k: sol4(k) for k in ("A2a", "A2b", "A2c")}, solves_16x16={k: S4[k]["solve16"] for k in ("A2a", "A2b", "A2c")},
               first_solved_median={k: S4[k]["medians"]["first_solved"] for k in ("A1a", "A1b", "A1c")},
               runs={k: S4[k]["run"] for k in ("A1a", "A1b", "A1c", "A2a", "A2b", "A2c")})
# C5 farming task-dependent
ex = r3["exploratory_rescore"]
farm_r2 = {t: v["counts"]["cycle-farm"] for t, v in ex.items() if t.startswith(("Agent 3: homeostatic", "N"))}
c["C5"] = dict(round2_rescored_cycle_farm=farm_r2, round2_n=10,
               round2_tests={k: v for k, v in r2["fisher"].items()}, round2_logistic=r2["logistic"],
               round3={k: r3["round3"][k]["counts"]["cycle-farm"] for k in r3["round3"]}, round3_tests=r3["tests"],
               round4_B5_B6=dict(B5=S4["B5"]["categories"]["cycle-farm"], B6=S4["B6"]["categories"]["cycle-farm"], test=dict(observed=P4["PB4"]["observed"], p=P4["PB4"]["p"])),
               keycorridor={k: S5[k]["categories"]["cycle-farm"] for k in ("C1", "C2", "C3", "C4")},
               keycorridor_tests={k: dict(observed=P5[k]["observed"], p=P5[k]["p"]) for k in ("C-P1", "C-P2")},
               n6_replay_intrinsic_return_per_episode={s: v["r_int"] for s, v in n6["seeds"].items()})
c["theory"] = dict(round3_vi_main=[dict(growth=x["growth"], gamma=x["gamma"], bin=x["bin"], outcome=x["outcome"], steps=x.get("steps")) for x in vi3 if x["bin"] == "g"],
                   round4_B0=[dict(growth=x["growth"], bin=x["bin"], tampers=x["tampers"], tamper_steps=x["tamper_steps"], steps=x["steps"]) for x in b0])
c["D"] = dict(D1=pd["D1"], D3=pd["D3"])
c["tallies"] = dict(round4=dict(rows=len(r4["predictions"]), hits=sum(x["hit"] is True for x in r4["predictions"])),
                    round5=dict(rows=len(r5["predictions"]), hits=sum(x["hit"] is True for x in r5["predictions"]), holm_m=r5["holm_m_abc"]))
out.write_text(json.dumps(c, indent=1, default=float)); print("written", out)
