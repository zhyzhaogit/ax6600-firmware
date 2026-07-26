from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


FEED_TARGETS = {
    "packages": "feeds/packages",
    "luci": "feeds/luci",
    "routing": "feeds/routing",
    "telephony": "feeds/telephony",
    "video": "feeds/video",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply required feed package patches and report exact hashes.")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--patch-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json-report", default="")
    return parser.parse_args()


def package_directory(source_root: Path, feed: str, package: str) -> Path:
    if feed not in FEED_TARGETS:
        raise ValueError(f"unknown feed {feed!r}")
    feed_root = source_root / FEED_TARGETS[feed]
    matches = sorted(path for path in feed_root.rglob(package) if path.is_dir() and (path / "Makefile").is_file())
    if not matches:
        raise ValueError(f"package {package!r} not found in feed {feed!r}")
    if len(matches) > 1:
        rendered = ", ".join(str(path.relative_to(source_root)) for path in matches)
        raise ValueError(f"package {package!r} is ambiguous in feed {feed!r}: {rendered}")
    return matches[0]


def patch_state(package_dir: Path, patch_file: Path) -> str:
    forward = subprocess.run(
        ["patch", "--dry-run", "--batch", "-p1", "-i", str(patch_file)],
        cwd=package_dir,
        capture_output=True,
        text=True,
    )
    if forward.returncode == 0:
        subprocess.run(
            ["patch", "--batch", "-p1", "-i", str(patch_file)],
            cwd=package_dir,
            check=True,
        )
        return "applied"

    reverse = subprocess.run(
        ["patch", "--dry-run", "--batch", "-R", "-p1", "-i", str(patch_file)],
        cwd=package_dir,
        capture_output=True,
        text=True,
    )
    if reverse.returncode == 0:
        return "already-applied"
    detail = (forward.stderr or forward.stdout).strip().splitlines()
    raise RuntimeError(detail[-1] if detail else "patch dry-run failed")


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).resolve()
    patch_root = Path(args.patch_root).resolve()
    report_path = Path(args.report).resolve()
    rows: list[str] = []
    failures: list[str] = []
    records: list[dict[str, str]] = []

    if patch_root.is_dir():
        for patch_file in sorted(patch_root.rglob("*.patch")):
            relative = patch_file.relative_to(patch_root)
            if len(relative.parts) < 3:
                digest = hashlib.sha256(patch_file.read_bytes()).hexdigest()
                failures.append(f"{relative}: expected <feed>/<package>/<patch>.patch")
                rows.append(
                    f"- `{relative.as_posix()}` `{digest}`: failed - expected <feed>/<package>/<patch>.patch"
                )
                records.append(
                    {
                        "path": relative.as_posix(),
                        "sha256": digest,
                        "status": "failed",
                        "detail": "expected <feed>/<package>/<patch>.patch",
                    }
                )
                continue
            feed, package = relative.parts[:2]
            digest = hashlib.sha256(patch_file.read_bytes()).hexdigest()
            try:
                target = package_directory(source_root, feed, package)
                state = patch_state(target, patch_file)
                rows.append(f"- `{relative.as_posix()}` `{digest}`: {state}")
                records.append(
                    {"path": relative.as_posix(), "sha256": digest, "status": state, "detail": ""}
                )
            except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
                failures.append(f"{relative.as_posix()}: {exc}")
                rows.append(f"- `{relative.as_posix()}` `{digest}`: failed - {exc}")
                records.append(
                    {
                        "path": relative.as_posix(),
                        "sha256": digest,
                        "status": "failed",
                        "detail": str(exc),
                    }
                )

    if not rows:
        rows.append("- no feed package patches declared")
    report = "\n".join(["# Feed Patch Report", "", *rows, ""])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    if args.json_report:
        json_path = Path(args.json_report).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {"status": "failed" if failures else "success", "patches": records},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    if failures:
        print("Required feed patches failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
