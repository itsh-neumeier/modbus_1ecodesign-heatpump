"""Ensure git tag and integration manifest version match."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_version.py <tag>")
        return 1

    tag = sys.argv[1]
    normalized_tag = tag[1:] if tag.startswith("v") else tag

    manifest_path = Path("custom_components/modbus_1ecodesign_heatpump/manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_version = manifest["version"]

    if normalized_tag != manifest_version:
        print(
            f"Version mismatch: tag='{tag}' vs manifest='{manifest_version}'. "
            "Expected format: vX.Y.Z and matching manifest version."
        )
        return 1

    print(f"Version validated: {normalized_tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

