from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from common import REPO_ROOT, load_yaml, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replace scaffold placeholders with your GitHub repository identity.")
    parser.add_argument("--github-user", required=True, help="GitHub username or organization")
    parser.add_argument("--source-repo-name", default="ax6600-source")
    parser.add_argument("--firmware-repo-name", default="ax6600-firmware")
    parser.add_argument("--enable-source-primary", action="store_true")
    parser.add_argument("--upstreams", default="targets/ax6600/upstreams.yml")
    return parser.parse_args()


def dump_yaml(payload: object) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)


def main() -> int:
    args = parse_args()
    upstreams_path = REPO_ROOT / args.upstreams
    upstreams = load_yaml(upstreams_path)

    source_primary = upstreams["repositories"]["source-primary"]
    source_primary["repo"] = f"{args.github_user}/{args.source_repo_name}"
    if args.enable_source_primary:
        source_primary["enabled"] = True

    note = (
        "Personal source repository configured by bootstrap_identity.py. "
        "Keep this in sync with your actual GitHub repository names."
    )
    source_primary["note"] = note

    write_text(upstreams_path, dump_yaml(upstreams))

    summary_lines = [
        "# Bootstrap Summary",
        "",
        f"- github user: `{args.github_user}`",
        f"- firmware repo name: `{args.firmware_repo_name}`",
        f"- source repo name: `{args.source_repo_name}`",
        f"- source-primary repo: `{source_primary['repo']}`",
        f"- source-primary enabled: `{source_primary['enabled']}`",
        "",
        "Next steps:",
        "",
        "1. Review `targets/ax6600/upstreams.yml`.",
        "2. Add Git remotes and push both repositories.",
        "3. Enable GitHub Actions and run `control-plane-check`.",
        "",
    ]
    write_text(REPO_ROOT / "reports/bootstrap-summary.md", "\n".join(summary_lines))
    print(source_primary["repo"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
