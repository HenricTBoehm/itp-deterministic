#!/usr/bin/env python3
"""Verify the local source and write the deterministic Phase A.4 JSON."""

from __future__ import annotations

import json
from pathlib import Path

from itp_opt.published_2026 import SOURCE_FILE, SOURCE_SHA256, audit_report, file_sha256


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source = root / SOURCE_FILE
    if not source.is_file():
        raise SystemExit(f"missing required 2026 PDF: {source}")
    actual = file_sha256(source)
    if actual != SOURCE_SHA256:
        raise SystemExit(f"source checksum mismatch: expected {SOURCE_SHA256}, got {actual}")
    destination = root / "results/published_2026_audit.json"
    destination.write_text(json.dumps(audit_report(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
