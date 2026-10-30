"""Step 0: copy, byte for byte, every saved result file the paper reads into paper2/data/sources.

The paper's generators read only these snapshots and repository files, never the artifacts directory, so the
draft can be rebuilt from the repository alone. Absolute local paths inside a source file (run directories and
the like, never numbers) are replaced by placeholders such as <openresearch>/ while copying; SOURCES.json records
both the original artifact's SHA256 and the scrubbed snapshot's SHA256, and SHA256SUMS lists the snapshots.
Re-running refuses to overwrite a snapshot whose source has changed unless --refresh is given.

Usage (repo root): EIR_ARTIFACTS=<artifacts directory> python3 paper2/scripts/snapshot_sources.py [--refresh]
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
SRC = P / "data" / "sources"
ART = Path(os.environ.get("EIR_ARTIFACTS", ""))
SCRUB = [(re.compile(rb"/Users/[^/\"\s]+/\.local/share/openresearch/"), b"<openresearch>/"),
         (re.compile(rb"/Users/[^/\"\s]+/Desktop/evolved-intrinsic-rewards/"), b"<repo>/"),
         (re.compile(rb"/(?:Users|home)/[^/\"\s]+/"), b"<home>/")]


def scrub(data):
    for pattern, placeholder in SCRUB:
        data = pattern.sub(placeholder, data)
    return data

FILES = {  # snapshot name: artifact path (relative to ART)
    "s1-numbers.json": "stage1/stage1-numbers.json",
    "s2-finalists.csv": "stage2-report/finalists.csv",
    "s2-per-run.csv": "stage2-report/per-run.csv",
    "s2-search-summary.json": "stage2-report/search-summary.json",
    "s2-search-selection.json": "stage2-report/search-selection.json",
    "s2-cost.json": "stage2-report/cost-and-attempt-summary.json",
    "s2-attempts.json": "stage2-report/attempt-accounting-check.json",
    "s2-interruptions.csv": "stage2-report/interruptions-and-controller-history.csv",
    "s2-report.md": "stage2-report/stage2-report.md",
    "s2pre-pinned-determinism.json": "stage2-review/pinned-determinism-summary.json",
    "s2x-candidates.csv": "stage3-report/exploratory-stage2/candidates.csv",
    "s2x-groups.csv": "stage3-report/exploratory-stage2/pooled-random-object-groups.csv",
    "s2x-correlations.csv": "stage3-report/exploratory-stage2/correlations.csv",
    "s2x-summary.json": "stage3-report/exploratory-stage2/exploratory-summary.json",
    "s3-cells.csv": "stage3-report/analysis/cells.csv",
    "s3-comparisons.csv": "stage3-report/analysis/registered-comparisons.csv",
    "s3-fisher.csv": "stage3-report/analysis/descriptive-fisher.csv",
    "s3-tamper.json": "stage3-report/analysis/registered-tamper.json",
    "s3-label.json": "stage3-report/analysis/descriptive-label.json",
    "s3-tamper-per-seed.csv": "stage3-report/analysis/tamper-per-seed-descriptives.csv",
    "s3-tamper-windows.csv": "stage3-report/analysis/tamper-window-series.csv",
    "s3-genomes.csv": "stage3-report/analysis/winner-genomes.csv",
    "s3-definitions.json": "stage3-report/analysis/definitions.json",
    "s3-per-seed.csv": "stage3-report/analysis/per-seed.csv",
    "s3-learning-curves.csv": "stage3-report/figures/learning-curves.csv",
    "s3-winner-hashes.json": "stage3-report/frozen/winner-hashes.json",
    "s3-cost.json": "stage3-report/cost/cost-summary.json",
    "s3-billing.json": "stage3-report/cost/billing-final-report-refresh.json",
    "s3-integrity.json": "stage3-report/integrity-check.json",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not (ART / "stage3-report").is_dir():
        raise SystemExit("Set EIR_ARTIFACTS to the project's artifacts directory")
    refresh = "--refresh" in sys.argv
    SRC.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, rel in FILES.items():
        raw = (ART / rel).read_bytes()
        clean, dst = scrub(raw), SRC / name
        if dst.exists() and sha(dst.read_bytes()) != sha(clean) and not refresh:
            raise SystemExit(f"{name}: source changed since the snapshot; inspect it, then rerun with --refresh")
        dst.write_bytes(clean)
        manifest[name] = {"artifact": rel, "artifact_sha256": sha(raw), "sha256": sha(clean), "bytes": len(clean),
                          "paths_scrubbed": clean != raw}
    (SRC / "SOURCES.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (SRC / "SHA256SUMS").write_text("".join(f"{v['sha256']}  {k}\n" for k, v in sorted(manifest.items())))
    print(f"{len(manifest)} snapshots, {sum(v['bytes'] for v in manifest.values()):,} bytes, "
          f"{sum(v['paths_scrubbed'] for v in manifest.values())} scrubbed of local paths")


if __name__ == "__main__":
    main()
