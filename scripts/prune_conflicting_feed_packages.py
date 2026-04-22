#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path


RULES = (
    {
        "reason": "Prefer sbwml/luci-app-mosdns feed pair over upstream feeds/packages mosdns to avoid APK file ownership conflicts.",
        "paths": (
            "feeds/packages/net/mosdns",
        ),
    },
)


def prune_conflicts(source_root: Path) -> list[str]:
    removed: list[str] = []
    for rule in RULES:
        for rel_path in rule["paths"]:
            target = source_root / rel_path
            if not target.exists():
                continue
            if target.is_dir():
                for child in sorted(target.rglob("*"), reverse=True):
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                for child in sorted(target.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                target.rmdir()
            else:
                target.unlink()
            removed.append(f"{rel_path} | {rule['reason']}")
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove known upstream feed packages that conflict with pinned third-party feeds."
    )
    parser.add_argument("--source-root", required=True, help="OpenWrt source tree root")
    parser.add_argument(
        "--report",
        default="",
        help="Optional markdown report path, relative to the current working directory",
    )
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    if not source_root.exists():
        raise SystemExit(f"source root does not exist: {source_root}")

    removed = prune_conflicts(source_root)
    lines = ["# Feed Conflict Prune Report", ""]
    if removed:
        lines.extend(f"- removed `{entry}`" for entry in removed)
    else:
        lines.append("- no known conflicting upstream feed packages were present")
    report = "\n".join(lines) + "\n"
    print(report, end="")

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
