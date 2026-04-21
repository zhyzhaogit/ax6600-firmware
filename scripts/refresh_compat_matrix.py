from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date

from common import REPO_ROOT, github_commit, load_yaml, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh compat-matrix reference_state from tracked upstreams.")
    parser.add_argument("--upstreams", default="targets/ax6600/upstreams.yml")
    parser.add_argument("--compat", default="targets/ax6600/compat-matrix.yml")
    parser.add_argument("--output", default="targets/ax6600/compat-matrix.yml")
    return parser.parse_args()


def yaml_dump(data: object) -> str:
    import yaml

    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


def main() -> int:
    args = parse_args()
    upstreams = load_yaml(REPO_ROOT / args.upstreams)
    compat = deepcopy(load_yaml(REPO_ROOT / args.compat))

    reference_state = compat.setdefault("reference_state", {})
    today = str(date.today())

    for key, entry in upstreams["repositories"].items():
        if not entry.get("enabled", False):
            continue

        latest = github_commit(entry["repo"], entry["branch"])
        reference_state[key] = {
            "repo": entry["repo"],
            "branch": entry["branch"],
            "last_observed_commit": latest["sha"],
            "last_compared_at": today,
        }

    write_text(REPO_ROOT / args.output, yaml_dump(compat))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
