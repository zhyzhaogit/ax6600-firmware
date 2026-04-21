from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import REPO_ROOT, github_raw, load_yaml, markdown_table, sha256_text, write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture and classify watched reference file changes.")
    parser.add_argument("--upstreams", default="targets/ax6600/upstreams.yml")
    parser.add_argument("--state", default="reports/reference-state.json")
    parser.add_argument("--output", default="reports/config-diff.md")
    return parser.parse_args()


def classify(path: str, content: str, protected_keywords: list[str]) -> str:
    lowered = f"{path}\n{content}".lower()
    if any(keyword in lowered for keyword in protected_keywords):
        return "blocked"
    if path.startswith(".github/workflows/"):
        return "workflow-absorb"
    if path.startswith("Config/") or path.endswith(".config") or path.endswith(".txt"):
        return "config-absorb"
    if path.endswith("Settings.sh") or path.endswith("Packages.sh"):
        return "ai-review"
    return "manual-review"


def main() -> int:
    args = parse_args()
    upstreams = load_yaml(REPO_ROOT / args.upstreams)
    state_path = REPO_ROOT / args.state
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    protected_keywords = upstreams["policy"]["protected_keywords"]
    rows: list[list[str]] = []
    current: dict[str, dict[str, dict[str, str]]] = {}

    for key in upstreams["policy"]["default_compare_targets"]:
        entry = upstreams["repositories"][key]
        current[key] = {}
        for watched_path in entry.get("watched_paths", []):
            try:
                content = github_raw(entry["repo"], entry["branch"], watched_path)
                digest = sha256_text(content)
                prior_digest = previous.get(key, {}).get(watched_path, {}).get("sha256")
                status = "changed" if digest != prior_digest else "unchanged"
                category = classify(watched_path, content, protected_keywords)
                current[key][watched_path] = {"sha256": digest, "category": category}
                rows.append([key, watched_path, category, status])
            except Exception as exc:  # noqa: BLE001
                current[key][watched_path] = {"sha256": "fetch-error", "category": "manual-review"}
                rows.append([key, watched_path, "manual-review", f"fetch-error: {exc}"])

    report = "\n".join(
        [
            "# Config Diff Report",
            "",
            markdown_table(["reference", "path", "classification", "status"], rows),
            "",
            "Classification guide:",
            "",
            "- `config-absorb`: likely config fragment input.",
            "- `workflow-absorb`: candidate workflow or automation idea.",
            "- `ai-review`: script or package logic that should be reviewed before adoption.",
            "- `blocked`: protected or risky area that should not be copied blindly.",
            "- `manual-review`: needs human or AI judgment.",
            "",
        ]
    )

    write_text(REPO_ROOT / args.output, report)
    write_json(state_path, current)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
