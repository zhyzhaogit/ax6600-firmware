from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import REPO_ROOT, load_yaml, markdown_table, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare measured metrics with benchmark policy.")
    parser.add_argument("--baseline", default="benchmarks/baseline.yml")
    parser.add_argument("--metrics", required=True, help="YAML or JSON metrics file")
    parser.add_argument("--output", default="reports/baseline-check.md")
    return parser.parse_args()


def load_metrics(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return load_yaml(path)


def value_for(metrics: dict, section: str, key: str):
    return metrics.get(section, {}).get(key)


def main() -> int:
    args = parse_args()
    baseline = load_yaml(REPO_ROOT / args.baseline)
    metrics = load_metrics(REPO_ROOT / args.metrics)

    rows: list[list[str]] = []
    failures: list[str] = []

    for section in ("performance_targets", "resource_thresholds"):
        for key, policy in baseline.get(section, {}).items():
            actual = value_for(metrics, section, key)
            threshold_min = policy.get("minimum")
            threshold_max = policy.get("maximum")

            if actual is None:
                status = "fail" if baseline["validation_policy"]["fail_on_missing_metrics"] else "warn"
                note = "missing metric"
            elif threshold_min is not None and actual < threshold_min:
                status = "fail"
                note = f"{actual} < minimum {threshold_min}"
            elif threshold_max is not None and actual > threshold_max:
                status = "fail"
                note = f"{actual} > maximum {threshold_max}"
            else:
                status = "pass"
                note = str(actual)

            if status == "fail":
                failures.append(f"{section}.{key}")

            rows.append([section, key, status, note])

    report = "\n".join(
        [
            "# Baseline Comparison",
            "",
            markdown_table(["section", "metric", "status", "details"], rows),
            "",
        ]
    )
    write_text(REPO_ROOT / args.output, report)
    if failures:
        print("Baseline check failed:", ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
