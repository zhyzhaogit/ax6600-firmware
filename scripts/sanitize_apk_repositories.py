from __future__ import annotations

import argparse
import re
from pathlib import Path


TARGETS = (
    "bin/targets/*/*/packages.adb",
    "build_dir/target-*/root-*/etc/apk/repositories",
)

DEFAULT_ALLOWED_FEEDS = {
    "base",
    "luci",
    "packages",
    "routing",
    "telephony",
    "video",
}

FEED_RE = re.compile(r"/packages/[^/]+/([^/]+)/packages\.adb$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Disable APK repository entries for local-only custom feeds that are compiled into the image."
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument(
        "--allowed-feeds",
        default=",".join(sorted(DEFAULT_ALLOWED_FEEDS)),
        help="Comma-separated feed names whose remote APK repositories should stay enabled.",
    )
    parser.add_argument("--report", default="")
    return parser.parse_args()


def classify_line(line: str, allowed_feeds: set[str]) -> tuple[str, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return line, "unchanged"

    match = FEED_RE.search(stripped)
    if not match:
        return line, "unchanged"

    feed = match.group(1)
    if feed in allowed_feeds:
        return line, "kept"
    return f"# {line}", f"disabled:{feed}"


def sanitize_file(path: Path, allowed_feeds: set[str]) -> list[str]:
    original = path.read_text(encoding="utf-8")
    output_lines: list[str] = []
    actions: list[str] = []

    for line in original.splitlines():
        new_line, action = classify_line(line, allowed_feeds)
        output_lines.append(new_line)
        if action.startswith("disabled:"):
            actions.append(f"{path}: {action.removeprefix('disabled:')}")

    updated = "\n".join(output_lines) + ("\n" if original.endswith("\n") else "")
    if updated != original:
        path.write_text(updated, encoding="utf-8")
    return actions


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).resolve()
    allowed_feeds = {item.strip() for item in args.allowed_feeds.split(",") if item.strip()}

    actions: list[str] = []
    for pattern in TARGETS:
        for path in source_root.glob(pattern):
            if path.is_file():
                actions.extend(sanitize_file(path, allowed_feeds))

    report_lines = ["# APK Repository Sanitize Report", ""]
    if actions:
        report_lines.extend(f"- {item}" for item in actions)
    else:
        report_lines.append("- no local-only APK repository entries needed changes")

    report = "\n".join(report_lines) + "\n"
    print(report, end="")

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
