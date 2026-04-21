from __future__ import annotations

import argparse

from common import REPO_ROOT, load_yaml, markdown_table, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check required feature policy against the repository and a config file.")
    parser.add_argument("--policy", default="targets/ax6600/feature-policy.yml")
    parser.add_argument("--config", default="build/ax6600/.config")
    parser.add_argument("--output", default="reports/required-features.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = load_yaml(REPO_ROOT / args.policy)
    config_path = REPO_ROOT / args.config
    config_text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""

    rows: list[list[str]] = []
    failures: list[str] = []

    for name, feature in policy["features"].items():
        level = feature["level"]
        config_markers = feature.get("config_markers", [])
        repo_markers = feature.get("repo_markers", [])

        missing_config = [marker for marker in config_markers if marker not in config_text]
        missing_repo = [marker for marker in repo_markers if not (REPO_ROOT / marker).exists()]

        if missing_config or missing_repo:
            status = "fail" if level == "required" else "warn"
        else:
            status = "pass"

        if status == "fail":
            failures.append(name)

        evidence = []
        if missing_config:
            evidence.append("missing config: " + ", ".join(missing_config))
        if missing_repo:
            evidence.append("missing repo: " + ", ".join(missing_repo))
        if not evidence:
            evidence.append("all required markers present")

        rows.append([name, level, status, "; ".join(evidence)])

    report = "\n".join(
        [
            "# Required Feature Report",
            "",
            markdown_table(["feature", "level", "status", "evidence"], rows),
            "",
        ]
    )
    write_text(REPO_ROOT / args.output, report)

    if failures:
        print("Missing required features:", ", ".join(failures))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
