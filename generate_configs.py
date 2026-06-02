#!/usr/bin/env python3
"""Generate JSON config files from the central configs.yaml manifest.

Usage:
    python generate_configs.py          # regenerate all configs
    python generate_configs.py --check  # verify configs are up-to-date (CI-friendly)

Each file entry in configs.yaml names a template and an overrides dict.
The generator merges template + overrides and writes pretty-printed JSON.
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required.  Install it with:  pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent
MANIFEST = REPO_ROOT / "configs.yaml"


def ordered_merge(template: dict, overrides: dict) -> OrderedDict:
    """Merge *overrides* into *template*, preserving insertion order.

    Keys from *template* come first; any extra keys in *overrides* that are
    not in the template are appended at the position where they logically
    belong (right after the last template key that precedes them
    alphabetically).  In practice, ``overrides`` is small and extra keys are
    simply appended at the end.
    """
    merged = OrderedDict(template)
    for key, value in overrides.items():
        merged[key] = value
    return merged


def build_config(templates: dict, file_spec: dict) -> OrderedDict:
    """Return the final merged config for one output file."""
    tpl_name = file_spec["template"]
    template = templates[tpl_name]
    overrides = file_spec.get("overrides") or {}
    return ordered_merge(template, overrides)


def generate(check_only: bool = False) -> bool:
    """Generate (or verify) all configs.  Returns True when everything is OK."""
    with open(MANIFEST) as fh:
        manifest = yaml.safe_load(fh)

    templates = manifest["templates"]
    files = manifest["files"]
    all_ok = True

    for filename, spec in files.items():
        config = build_config(templates, spec)
        rendered = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        target = REPO_ROOT / filename
        if check_only:
            if not target.exists():
                print(f"MISSING  {filename}")
                all_ok = False
            elif target.read_text() != rendered:
                print(f"STALE    {filename}")
                all_ok = False
            else:
                print(f"OK       {filename}")
        else:
            target.write_text(rendered)
            print(f"wrote    {filename}")

    return all_ok


if __name__ == "__main__":
    check = "--check" in sys.argv
    ok = generate(check_only=check)
    if check and not ok:
        print("\nSome configs are out of date.  Run `python generate_configs.py` to fix.")
        sys.exit(1)
