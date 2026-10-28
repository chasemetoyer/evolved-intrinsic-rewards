"""Verify unchanged local release bytes against its manifest, ZIP, and Zenodo."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "handoff-cross-platform/paper-impact-audit"
OUT = Path("/Users/chasemetoyer/.local/share/openresearch/files/evolved-intrinsic-rewards/paper-impact-audit")


def main():
    release = BASE / "release"
    archive = BASE / "release.zip"
    entries = []
    for line in (release / "SHA256SUMS").read_text().splitlines():
        sha, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        p = release / name
        entries.append(dict(path=name, expected=sha,
                            actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None))
    mismatches = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.removeprefix("release/")
            p = release / name
            if not p.is_file() or hashlib.sha256(z.read(info)).digest() != hashlib.sha256(p.read_bytes()).digest():
                mismatches.append(name)
    remote = json.loads((BASE / "zenodo-record.json").read_text())
    item = next(f for f in remote["files"] if f["key"] == "release.zip")
    raw = archive.read_bytes()
    remote_match = (item["checksum"] == "md5:" + hashlib.md5(raw).hexdigest()
                    and item["size"] == len(raw))
    data = dict(archive_sha256=hashlib.sha256(raw).hexdigest(), archive_size_bytes=len(raw),
                manifest_entries=len(entries), manifest_failures=[e for e in entries if e["expected"] != e["actual"]],
                zip_vs_extracted_mismatches=mismatches, remote_zenodo_checksum_verified=remote_match,
                zenodo_doi=remote["doi"], zenodo_checksum=item["checksum"], files=entries)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "archive-integrity.json").write_text(json.dumps(data, indent=2) + "\n")
    assert not data["manifest_failures"] and not mismatches and remote_match, "Archive integrity failed"
    print(json.dumps({k: v for k, v in data.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
