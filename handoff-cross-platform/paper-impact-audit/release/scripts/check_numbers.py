"""Step 3: check every number in the paper against the source files. Reports mismatches; exit code 1 if any.

Checks, in order:
  1. Regenerate the number macros (make_numbers.py) and every table (make_tables.py) in memory from
     paper/data/sources and paper/data, and compare them with the committed paper/numbers.tex and paper/tables/*.tex.
  2. Verify the snapshots in paper/data/sources against their SHA256SUMS, and the pre-registration hashes against
     the records written at locking.
  3. Cross-check headline values against an independent extraction: paper/data/claims.json, which was produced
     earlier by extract_claims.py from the artifacts directory (a different code path from make_numbers.py).
  4. Every \\val{key} used in main.tex is defined.
  5. Scan the prose of main.tex for literal numbers. Every measured value must come through \\val; a literal is
     accepted only if it is a declared design constant (ALLOWED below, with its justification) or sits inside a
     declared fixed phrase (PHRASES). Anything else is reported.
  6. Bibliography: every entry has a DOI or an arXiv identifier, every cited key exists, and every arXiv id appears
     in main.bbl.
  7. No internal run IDs (B10, K5, A-P2m, ...) in the main text or its tables; they belong in the appendix map.
  8. Counts written as words ("two of three", "all four", "every seed", ...) cannot be traced automatically. Each
     occurrence is identified by its surrounding words and must appear in paper/data/worded-counts.json, the list of
     occurrences confirmed by hand against the data, with the evidence for each. A new or edited occurrence is
     reported until it is confirmed. After checking new occurrences by hand, `--confirm-worded` adds them to the list
     with evidence "TO FILL", which must then be replaced.

Usage note: a pass means every digit in the prose is a generated value or a declared constant, every generated value
matches the sources, and every worded count was confirmed by hand. It does not check that the words around a number
describe it correctly; that is what self-review and reading are for.

Usage (repo root): uv run --isolated --no-project --with numpy --with scipy python paper/scripts/check_numbers.py
"""
import hashlib, json, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_numbers, make_tables  # noqa: E402

P = HERE.parent
SRC, DATA = P / "data" / "sources", P / "data"
problems, notes = [], []


def bad(msg):
    problems.append(msg)


# ------------------------------------------------------------------ 1. regenerate macros and tables
with tempfile.TemporaryDirectory() as tmp:
    make_tables.OUT = Path(tmp)
    summary = make_tables.main()
    for f in sorted(Path(tmp).glob("*.tex")):
        committed = P / "tables" / f.name
        if not committed.exists():
            bad(f"table {f.name}: generated but not committed")
        elif committed.read_text() != f.read_text():
            bad(f"table {f.name}: committed file differs from regenerated output")
    for f in sorted((P / "tables").glob("*.tex")):
        if not (Path(tmp) / f.name).exists():
            bad(f"table {f.name}: committed but no longer generated")
committed_summary = json.loads((DATA / "tables-summary.json").read_text())
if committed_summary != summary:
    bad(f"tables-summary.json differs from regenerated summary {summary}")
make_numbers.V.clear()
tex, js = make_numbers.main()
if (P / "numbers.tex").read_text() != tex:
    old = set((P / "numbers.tex").read_text().splitlines()); new = set(tex.splitlines())
    for l in sorted(old - new)[:20]:
        bad(f"numbers.tex has a stale line: {l}")
    for l in sorted(new - old)[:20]:
        bad(f"numbers.tex is missing regenerated line: {l}")
vals = {k: v["text"] for k, v in json.loads(js).items()}
notes.append(f"regenerated {len(vals)} number macros and {len(list((P / 'tables').glob('*.tex')))} tables")

# ------------------------------------------------------------------ 2. snapshot integrity and lock records
for line in (SRC / "SHA256SUMS").read_text().splitlines():
    h, fn = line.split(maxsplit=1)
    if hashlib.sha256((SRC / fn).read_bytes()).hexdigest() != h:
        bad(f"snapshot {fn}: sha256 differs from SHA256SUMS")
for r in ("3", "4", "5"):
    rec = (SRC / f"round{r}-preregistration.sha256").read_text().split()[0]
    if hashlib.sha256((SRC / f"round{r}-preregistration.md").read_bytes()).hexdigest() != rec:
        bad(f"round {r} pre-registration snapshot does not match its lock record")

# ------------------------------------------------------------------ 3. independent cross-check against claims.json
C = json.loads((DATA / "claims.json").read_text())
fp = make_numbers.fp
cross = {
    "r4.solve.B1": f"{C['C1']['doorkey_round4']['tamper_on']['B1']}/20",
    "r4.solve.B2": f"{C['C1']['doorkey_round4']['tamper_on']['B2']}/20",
    "r4.solve.B3": f"{C['C1']['doorkey_round4']['tamper_on']['B3']}/20",
    "r4.solve.B4": f"{C['C1']['doorkey_round4']['tamper_on']['B4']}/20",
    "r4.solve.A1b": f"{C['C1']['doorkey_round4']['tamper_off']['A1b']}/20",
    "r4.solve.B7": f"{C['C1']['doorkey_round4']['tamper_off']['B7']}/20",
    "r4.solve.B5": f"{C['C1']['doorkey_round4']['tamper_off']['B5']}/20",
    "r4.solve.B6": f"{C['C1']['doorkey_round4']['tamper_off']['B6']}/20",
    "r4.solve.on": f"{sum(C['C1']['doorkey_round4']['tamper_on'].values())}/80",
    "r4.solve.off": f"{sum(C['C1']['doorkey_round4']['tamper_off'].values())}/80",
    "r5.solve.B9": f"{C['C1']['doorkey_round5_B9']['solve']}/20",
    "r5.solve.C5": f"{C['C1']['keycorridor_C5']['solve']}/20",
    "r5.solve.C1": f"{C['C1']['keycorridor_C5']['C1']}/20",
    "r5.solve.C6": f"{C['C1']['keycorridor_C5']['C6']}/20",
    "r5.solve.A1": f"{C['C2']['A1_solve']}/20",
    "r5.solve.A2": f"{C['C2']['A2_solve']}/20",
    "r5.auc.A1": f"{C['C2']['A1_auc']:.3f}",
    "r5.auc.r4B1": f"{C['C2']['B1_auc']:.3f}",
    "r5.auc.A2": f"{C['C2']['A2_auc']:.3f}",
    "r5.auc.r4B2": f"{C['C2']['B2_auc']:.3f}",
    "r5.solve.B1B3": f"{C['C2']['B1B3_solve']}/40",
    "r5.auc.B9": f"{C['C3']['auc']['B9']:.3f}",
    "r5.auc.B10": f"{C['C3']['auc']['B10']:.3f}",
    "r5.auc.B11": f"{C['C3']['auc']['B11']:.3f}",
    "r5.auc.r4A1b": f"{C['C3']['auc']['r4-A1b']:.3f}",
    "r5.tamperers.B10": f"{C['C3']['tamperers']['B10']}/20",
    "s0.160.tamper": f"{C['C3']['step0']['1/160']['largest_c_still_tampers']:.4f}".rstrip("0"),
    "s0.40.tamper": f"{C['C3']['step0']['1/40']['largest_c_still_tampers']:.4f}".rstrip("0"),
    "r4.fs.A1a": f"{int(C['C4']['first_solved_median']['A1a']):,}",
    "r4.fs.A1b": f"{int(C['C4']['first_solved_median']['A1b']):,}",
    "r4.fs.A1c": f"{int(C['C4']['first_solved_median']['A1c']):,}",
    "r4.curve8.A2a": f"{C['C4']['curve_means']['A2a']['DoorKey-8x8']:.3f}",
    "r4.curve8.A2b": f"{C['C4']['curve_means']['A2b']['DoorKey-8x8']:.3f}",
    "r4.curve8.A2c": f"{C['C4']['curve_means']['A2c']['DoorKey-8x8']:.3f}",
    "r4.curve16.A2a": f"{C['C4']['curve_means']['A2a']['DoorKey-16x16']:.3f}",
    "r4.curve16.A2b": f"{C['C4']['curve_means']['A2b']['DoorKey-16x16']:.3f}",
    "r4.curve16.A2c": f"{C['C4']['curve_means']['A2c']['DoorKey-16x16']:.3f}",
    "r4.solve.A2a": f"{C['C4']['solves_8x8']['A2a']}/20",
    "r4.solve.A2b": f"{C['C4']['solves_8x8']['A2b']}/20",
    "r4.solve.A2c": f"{C['C4']['solves_8x8']['A2c']}/20",
    "r4.solve16.A2a": f"{C['C4']['solves_16x16']['A2a']}/20",
    "r4.solve16.A2b": f"{C['C4']['solves_16x16']['A2b']}/20",
    "r4.solve16.A2c": f"{C['C4']['solves_16x16']['A2c']}/20",
    "r3.farm.R1": f"{C['C5']['round3']['R1']}/20",
    "r3.farm.R2": f"{C['C5']['round3']['R2']}/20",
    "r3.farm.R4": f"{C['C5']['round3']['R4']}/20",
    "r3.farm.R9": f"{C['C5']['round3']['R9']}/20",
    "r3.normoff.total": f"{sum(C['C5']['round3'][k] for k in ('R6', 'R7', 'R8'))}/60",
    "r3.normon.total": f"{sum(C['C5']['round3'][k] for k in ('R3', 'R4', 'R5'))}/60",
    "r4.farm.B5": f"{C['C5']['round4_B5_B6']['B5']}/20",
    "r4.farm.B6": f"{C['C5']['round4_B5_B6']['B6']}/20",
    "r2.rescore.N6": f"{C['C5']['round2_rescored_cycle_farm']['N6: growth 1/20']}/10",
    "r2.rescore.N1": f"{C['C5']['round2_rescored_cycle_farm']['N1: anchor replicate, growth 1/40, seeds 10-19']}/10",
    "r2.rescore.N3": f"{C['C5']['round2_rescored_cycle_farm']['N3: growth 1/80']}/10",
    "r5.farm.C1": f"{C['C5']['keycorridor']['C1']}/20",
    "r5.farm.C3": f"{C['C5']['keycorridor']['C3']}/20",
    "r5.farm.C4": f"{C['C5']['keycorridor']['C4']}/20",
    "d2.on.B1": f"{C['C1']['entropy_D2']['B1>A1b']['median_on']:.3f}",
    "d2.on.B2": f"{C['C1']['entropy_D2']['B2>B7']['median_on']:.3f}",
    "d2.on.B3": f"{C['C1']['entropy_D2']['B3>B5']['median_on']:.3f}",
    "d2.on.B4": f"{C['C1']['entropy_D2']['B4>B6']['median_on']:.3f}",
    "d2.off.A1b": f"{C['C1']['entropy_D2']['B1>A1b']['median_off']:.3f}",
    "d2.off.B7": f"{C['C1']['entropy_D2']['B2>B7']['median_off']:.3f}",
    "d2.off.B5": f"{C['C1']['entropy_D2']['B3>B5']['median_off']:.3f}",
    "d2.off.B6": f"{C['C1']['entropy_D2']['B4>B6']['median_off']:.3f}",
    "ln7": f"{C['C1']['uniform_entropy_ln7']:.3f}",
    "d1.declined": f"{C['D']['D1']['found_then_lost_declined']}/{C['D']['D1']['found_then_lost_n']}",
    "d1.firstgoal.median": f"{int(C['D']['D1']['first_goal_median']):,}",
    "d3.rise": f"{C['D']['D3']['rise_first']}/{C['D']['D3']['seeds_with_both']}",
    "p.PB2-B1": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B1"]["p"]),
    "p.PB2-B2": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B2"]["p"]),
    "p.PB2-B3": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B3"]["p"]),
    "p.PB2-B4": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B4"]["p"]),
    "ph.PB2-B1": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B1"]["p_holm"]),
    "ph.PB2-B3": fp(C["C1"]["doorkey_round4"]["tests"]["PB2-B3"]["p_holm"]),
    "p.B-F-B9-vsA1b": fp(C["C1"]["doorkey_round5_B9"]["test"]["p"]),
    "p.C-P3": fp(C["C1"]["keycorridor_C5"]["tests"]["C-P3"]["p"]),
    "p.C-P4": fp(C["C1"]["keycorridor_C5"]["tests"]["C-P4"]["p"]),
    "ph.C-P3": fp(C["C1"]["keycorridor_C5"]["tests"]["C-P3"]["p_holm"]),
    "p.D2": fp(C["C1"]["entropy_D2"]["B1>A1b"]["p"]),
    "p.D3": fp(C["D"]["D3"]["p_binom"]),
    "p.PB4": fp(C["C5"]["round4_B5_B6"]["test"]["p"]),
    "p.C-P1": fp(C["C5"]["keycorridor_tests"]["C-P1"]["p"]),
    "p.C-P2": fp(C["C5"]["keycorridor_tests"]["C-P2"]["p"]),
    "p.N6>N3": fp(C["C5"]["round2_tests"]["N6 > N3"]["p"]),
    "p.N2<N1": fp(C["C5"]["round2_tests"]["N2 < N1"]["p"]),
    "p.R1<R4": fp(C["C5"]["round3_tests"]["R1 < R4 (Fisher, one-sided)"]),
    "p.R2>R4": fp(C["C5"]["round3_tests"]["R2 > R4 (Fisher, one-sided)"]),
    "p.R9<R4": fp(C["C5"]["round3_tests"]["R9 < R4 (Fisher, one-sided)"]),
    "p.r2logistic": fp(C["C5"]["round2_logistic"]["p_one_sided"]),
}
for t in ("A-P1", "A-P1m", "A-P2", "A-P2m", "A-P3", "A-P3m"):
    cross[f"p.{t}"] = fp(C["C2"]["tests"][t]["p"])
for t in ("B-JTp", "B-JTs", "B-F-B10-vsB1", "B-F-B11-vsB1"):
    cross[f"p.{t}"] = fp(C["C3"]["tests"][t]["p"])
for t in ("A1-P1", "A1-P2", "A2-P1", "A2-P2", "A2-P3", "A2-P4", "A2-P5", "A2-P6", "A2-P7", "A2-P8"):
    cross[f"p.{t}"] = fp(C["C4"]["tests"][t]["p"])
mism = 0
for k, want in cross.items():
    if k not in vals:
        bad(f"cross-check: {k} missing from the regenerated macros")
    elif vals[k] != want:
        mism += 1
        bad(f"cross-check: {k} = {vals[k]!r} but claims.json gives {want!r}")
notes.append(f"cross-checked {len(cross)} values against claims.json ({mism} mismatches)")

# ------------------------------------------------------------------ 4. every \val used is defined
main = (P / "main.tex").read_text()
body = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in main.splitlines())   # strip comments, keep \%
body = body.replace(r"\%", "PERCENT").split(r"\begin{document}")[1]            # the document only, not the preamble
used = set(re.findall(r"\\val\{([^}]+)\}", body))
used |= {"p." + k for k in re.findall(r"\\pv\{([^}]+)\}", body)}
used |= {"ph." + k for k in re.findall(r"\\ph\{([^}]+)\}", body)}
for k in sorted(used - set(vals)):
    bad(f"main.tex uses undefined value {k}")
notes.append(f"main.tex uses {len(used)} distinct values; {len(set(vals) - used)} generated values are not cited in the prose")

# ------------------------------------------------------------------ 5. literal numbers in the prose
# Design constants: (literal, justification). Accepted anywhere in the prose.
ALLOWED = {
    "0.75": "D(h0) = 3 x 0.5^2, the ceiling (Proposition 1)", "0.5": "h0, the starting need",
    "0.99": "discount", "0.95": "second discount tested by value iteration and in round 2",
    "640": "DoorKey-8x8 time limit", "270": "KeyCorridorS3R1 time limit", "2M": "environment steps per seed",
    "0.01": "tamper cost (round 5)", "0.1": "tamper cost (round 5); explore relief", "0.9": "solve threshold; MiniGrid reward",
    "0.10": "D1 peak-success threshold", "0.05": "D3 rise offset", "200k": "Part D checkpoint",
    "1/640": "growth", "1/160": "growth", "1/80": "growth", "1/60": "growth", "1/40": "growth", "1/30": "growth",
    "1/20": "growth", "1/10": "growth", "1/6": "growth", "1/4": "growth", "1/2": "growth", "1/7": "uniform press rate",
    "10PERCENT": "final 10% of training", "20PERCENT": "registered D1-P2 threshold", "95PERCENT": "interval level",
    "10000": "first layout seed", "10199": "last layout seed", "10{,}000": "bootstrap resamples",
    "16": "parallel environments; 16 fixed layouts", "25": "evaluation points", "12": "CPU cores", "24": "GB memory",
    "20": "seeds per run", "0--9": "seeds", "10--19": "seeds", "20--39": "seeds", "40--59": "seeds", "60--79": "seeds",
    "2--5": "rounds", "10000--10199": "layout seeds (bound check)",
}
# Fixed phrases whose digits are structural (counts of conditions, round numbers, grid sizes, identifiers).
PHRASES = [
    r"rounds? [1-5]", r"rounds [2-5]--[2-5]", r"[Rr]ound-[1-5]", r"Round [1-5]", r"correction \d+", r"corrections \d+ and \d+",
    r"7\$\\times\$7(\$\\times\$3)?", r"7\$\\times\$5", r"8\$\\times\$8", r"16\$\\times\$16", r"2\$\\times\$2",
    r"\(0\.1,1,1\)", r"\$h_0=0\.5\$", r"\$1-0\.9\\,t/T\$", r"10\^\{-3\}", r"10\^\{-7\}", r"\$\\gamma=0\.99\$",
    r"\$D\(h_0\)=0\.75\$", r"\$D_0=0\.75\$", r"\$\\gamma\\in\(0,1\]\$", r"\$t=0\$", r"\$c=\\val", r"\$g=\\val",
    r"has 7 actions", r"seventh action", r"16 parallel environments", r"2M environment steps",
    r"more than 5", r"at least 1 press", r"more than 5 times", r"threshold \(5\)", r"1 step in 7",
    r"three needs", r"two of three", r"\(16, 32 and 64 channels", r"64-unit", r"one 2\$\\times\$2 max-pool",
    r"Apple M4 Pro", r"12 CPU cores, 24\\,GB", r"coef \$=1\$", r"coef \$=0\$", r"coef 1", r"coefficient 1",
    r"cost 0\.01", r"costs 0\.01, 0\.1 and 1", r"cost 0\.1", r"cost 1\b", r"cost of 0\.1", r"press cost of 0\.01",
    r"\(i+\)", r"\(iv\)", r"\(\d\)", r"Part~\(iii\)", r"seeds 40--59", r"1/7 \+ 0\.05", r"\$1/7 \+ 0\.05\$",
    r"25 evaluation points on 16 fixed fresh layouts", r"10\{,\}000 resamples", r"at 200k steps",
    r"zero cost", r"Step-0", r"Step 0", r"GPT", r"[A-Z]+[0-9]", r"\\ln 7",
    r"and 0 otherwise", r"\(growth 0\)", r"cost 0\b", r"coefficients 0\.5, 1 and 2", r"farmers of 10",
    r"\(10 in round 2\)", r"1/\\sqrt", r"\\in\[0,1\]", r"\\in\\\{0,1\\\}", r"=0\$", r"\\geq 0\$", r"\\leq 1\$",
    r"\(1-\\gamma\)", r"\$1-0\.9", r"D\(h_0\)=0\.75",
]
prose = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", body, flags=re.S)   # display definitions
prose = re.sub(r"10\^\{-[37]\}", " TENEXP ", prose)   # design constants: novelty coef 1e-3, VI tolerance 1e-7
prose = re.sub(r"[_^]\{[^{}]*\}", " ", prose)        # sub/superscripts (indices such as t+1, T-1)
prose = re.sub(r"[_^][0-9A-Za-z]", " ", prose)
for cmd in (r"\\label\{[^}]*\}", r"\\ref\{[^}]*\}", r"\\eqref\{[^}]*\}", r"\\cite[pt]?\{[^}]*\}", r"\\input\{[^}]*\}",
            r"\\includegraphics\[[^\]]*\]\{[^}]*\}", r"\\val\{[^}]*\}", r"\\pv\{[^}]*\}", r"\\ph\{[^}]*\}",
            r"\\begin\{(tabular|longtable)\}\{[^\n]*\}", r"\\nolinkurl\{[^}]*\}", r"\\texttt\{[^}]*\}",
            r"\[label=[^\]]*\]", r"\[itemsep=[^\]]*\]", r"\[leftmargin=[^\]]*\]", r"\\(begin|end)\{[^}]*\}",
            r"width=5\.5in", r"\[!?[htbp]+\]", r"\\textsuperscript\{[^}]*\}"):
    prose = re.sub(cmd, " ", prose)
prose = re.sub(r"\s+", " ", prose)                 # line breaks inside phrases
covered = [False] * len(prose)
for ph in PHRASES:
    for m in re.finditer(ph, prose):
        for i in range(m.start(), m.end()):
            covered[i] = True
unacc = []
tok = re.compile(r"(?<![A-Za-z0-9_.\\-])(\d+(?:\{,\}\d{3})*(?:[.,]\d+)?(?:/\d+)?(?:--\d+)?(?:PERCENT|k|M)?)(?![A-Za-z0-9])")
for m in tok.finditer(prose):
    s = m.group(1)
    if s in ALLOWED or all(covered[m.start():m.end()]):
        continue
    ctx = prose[max(0, m.start() - 40):m.end() + 25].replace("\n", " ")
    unacc.append((s, ctx))
for s, ctx in unacc:
    bad(f"literal number {s!r} in prose is neither a \\val nor a declared constant: ...{ctx}...")
notes.append(f"literal-number scan: {len(unacc)} unaccounted literals")

# ------------------------------------------------------------------ 6. bibliography
bib = (P / "references.bib").read_text()
entries = re.findall(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S)
keys = {k for k, _ in entries}
bbl = (P / "main.bbl").read_text() if (P / "main.bbl").exists() else ""
for k, b in entries:
    doi = re.search(r"\bdoi\s*=\s*\{([^}]+)\}", b); arx = re.search(r"\beprint\s*=\s*\{([^}]+)\}", b)
    if not doi and not arx:
        bad(f"bib entry {k} has neither a DOI nor an arXiv id")
    if arx and arx.group(1) not in bbl:
        bad(f"bib entry {k}: arXiv {arx.group(1)} does not appear in main.bbl (rebuild, or the style dropped it)")
cited = set()
for c in re.findall(r"\\cite[pt]?\{([^}]+)\}", body):
    cited |= {x.strip() for x in c.split(",")}
for k in sorted(cited - keys):
    bad(f"cited key {k} is not in references.bib")
for k in sorted(keys - cited):
    notes.append(f"bib entry {k} is not cited (it will not print)")
notes.append(f"bibliography: {len(keys)} entries, {len(cited)} cited")

# ------------------------------------------------------------------ 7. no internal run IDs in the main text
main_body = body.split(r"\appendix")[0]
main_tables = "".join((P / "tables" / f"{n}.tex").read_text() for n in ("bound", "replay", "cost", "farming", "accounting"))
idscan = re.sub(r"\\(val|pv|ph|label|ref|eqref|input|cite[pt]?|includegraphics)(\[[^\]]*\])?\{[^}]*\}", " ", main_body + main_tables)
idscan = re.sub(r"\\subsection\{C[1-5]:", " ", idscan)        # claim labels C1-C5 in headings are intended
ID = re.compile(r"\b(A1[abc]?|A2[abc]?|B\d+|C[1-6]|K[1-6]|R\d+|N[1-6]|PB\d|A-P\d+m?|B-[A-Z][A-Za-z0-9-]*|C-P\d|D[1-3]-P\d)\b")
for m in ID.finditer(idscan):
    bad(f"internal run ID {m.group(0)!r} in the main text: ...{idscan[max(0, m.start() - 50):m.end() + 30]}...".replace("\n", " "))

# ------------------------------------------------------------------ 8. worded counts confirmed by hand
WORDS = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|both|once|twice|half|single|"
                   r"none|no seed|every seed|all seeds|each of the|almost every seed)\b", re.I)
def plain(x):
    x = re.sub(r"\\(val|pv|ph)\{[^}]*\}", " N ", x)
    x = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?", " ", x)
    x = re.sub(r"[{}$~\\]", " ", x)
    return re.sub(r"\s+", " ", x).strip().lower()
flat = plain(body)
contexts = []
for m in WORDS.finditer(flat):
    pre = flat[:m.start()].split()[-3:]; post = flat[m.end():].split()[:3]
    contexts.append(" ".join(pre + [m.group(0).lower()] + post))
wfile = DATA / "worded-counts.json"
confirmed = json.loads(wfile.read_text()) if wfile.exists() else {}
new_ctx = [c for c in contexts if c not in confirmed]
if "--confirm-worded" in sys.argv and new_ctx:
    for c in new_ctx:
        confirmed[c] = "TO FILL"
    wfile.write_text(json.dumps(dict(sorted(confirmed.items())), indent=1))
    notes.append(f"added {len(new_ctx)} worded counts to {wfile.name} with evidence 'TO FILL'")
else:
    for c in new_ctx:
        bad(f"worded count not yet confirmed by hand: '{c}'")
for c, ev in confirmed.items():
    if ev == "TO FILL":
        bad(f"worded count '{c}' has no evidence recorded in {wfile.name}")
stale = [c for c in confirmed if c not in contexts]
notes.append(f"worded counts: {len(contexts)} occurrences, {len(contexts) - len(new_ctx)} confirmed by hand"
             + (f"; {len(stale)} confirmed entries no longer occur" if stale else ""))

# ------------------------------------------------------------------ report
for n in notes:
    print("note:", n)
if problems:
    print(f"\n{len(problems)} PROBLEM(S):")
    for p_ in problems:
        print("  -", p_)
    sys.exit(1)
print("\nall checks passed: every digit in the prose is a generated value (matching the sources) or a declared constant,"
      " and every worded count is confirmed by hand")
