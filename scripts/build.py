#!/usr/bin/env python3
"""Build deterministic source and plugin ZIPs from the explicit file allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

from validate import DISTRIBUTION_FILES, PLUGIN_NAME, contained_path, validate

FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def write_archive(root: Path, target: Path, prefix: str) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(DISTRIBUTION_FILES):
            source = contained_path(root, "./" + name)
            info = zipfile.ZipInfo(prefix + name, date_time=FIXED_TIMESTAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("Build refused because validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    version = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    output = args.out_dir.resolve() if args.out_dir else root / "dist"
    output.mkdir(parents=True, exist_ok=True)
    checksums = []
    for kind, prefix in (("source", f"{PLUGIN_NAME}/"), ("plugin", "")):
        target = output / f"{PLUGIN_NAME}-{version}-{kind}.zip"
        write_archive(root, target, prefix)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {target.name}\n")
        print(f"Built {target.name}: {len(DISTRIBUTION_FILES)} files, {target.stat().st_size} bytes")
    (output / "SHA256SUMS").write_text("".join(checksums), encoding="utf-8")
    print("Wrote SHA256SUMS. No host configuration or remote service was changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
