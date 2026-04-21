from __future__ import annotations

import argparse

from common import REPO_ROOT, github_commit, load_yaml, markdown_table, write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch upstream repositories for new commits.")
    parser.add_argument("--upstreams", default="targets/ax6600/upstreams.yml")
    parser.add_argument("--compat", default="targets/ax6600/compat-matrix.yml")
    parser.add_argument("--output", default="reports/sync-watch.md")
    parser.add_argument("--json-output", default="reports/sync-watch.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    upstreams = load_yaml(REPO_ROOT / args.upstreams)
    compat = load_yaml(REPO_ROOT / args.compat)
    previous = compat.get("reference_state", {})

    rows: list[list[str]] = []
    updates: list[dict] = []

    for key, entry in upstreams["repositories"].items():
        if not entry.get("enabled", False):
            continue

        prior_commit = previous.get(key, {}).get("last_observed_commit", "unknown")
        try:
            latest = github_commit(entry["repo"], entry["branch"])
            status = "updated" if latest["sha"] != prior_commit else "unchanged"

            if status == "updated":
                updates.append(
                    {
                        "key": key,
                        "repo": entry["repo"],
                        "branch": entry["branch"],
                        "latest_sha": latest["sha"],
                        "previous_sha": prior_commit,
                        "message": latest["message"],
                    }
                )

            rows.append(
                [
                    key,
                    entry["repo"],
                    entry["branch"],
                    latest["sha"][:12],
                    prior_commit[:12] if prior_commit != "unknown" else "unknown",
                    status,
                ]
            )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                [
                    key,
                    entry["repo"],
                    entry["branch"],
                    "error",
                    prior_commit[:12] if prior_commit != "unknown" else "unknown",
                    f"error: {exc}",
                ]
            )

    report_lines = [
        "# Sync Watch Report",
        "",
        markdown_table(["key", "repo", "branch", "latest", "previous", "status"], rows),
        "",
    ]
    if updates:
        report_lines.append("## Recommended Next Step")
        report_lines.append("")
        report_lines.append("Open a review PR, regenerate config and diff reports, and run canary validation before merging.")
    else:
        report_lines.append("No tracked upstream moved relative to the compatibility matrix snapshot.")

    write_text(REPO_ROOT / args.output, "\n".join(report_lines) + "\n")
    write_json(REPO_ROOT / args.json_output, {"updates": updates})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
