from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from common import REPO_ROOT, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record exact inputs and outputs for an AX6600 build.")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--patch-root", default="patches/firmware-layer")
    parser.add_argument("--patch-report", default="")
    parser.add_argument("--artifact-root", default="")
    parser.add_argument("--output", default="dist/release/build-provenance.json")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def feed_provenance(source_root: Path) -> list[dict[str, str]]:
    feeds_root = source_root / "feeds"
    feeds: list[dict[str, str]] = []
    if not feeds_root.is_dir():
        return feeds
    for feed_dir in sorted(path for path in feeds_root.iterdir() if path.is_dir()):
        try:
            commit = git_value(feed_dir, "rev-parse", "HEAD")
            remote = git_value(feed_dir, "remote", "get-url", "origin")
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        feeds.append({"name": feed_dir.name, "repository": remote, "commit": commit})
    return feeds


def hashed_files(root: Path) -> list[dict[str, str | int]]:
    if not root.is_dir():
        return []
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).resolve()
    config_path = Path(args.config).resolve()
    patch_root = (REPO_ROOT / args.patch_root).resolve()
    artifact_root = Path(args.artifact_root).resolve() if args.artifact_root else None
    patch_report = None
    if args.patch_report:
        patch_report = json.loads((REPO_ROOT / args.patch_report).read_text(encoding="utf-8"))

    payload = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": args.source_repo,
            "configured_branch": args.source_branch,
            "requested_ref": args.source_ref,
            "commit": git_value(source_root, "rev-parse", "HEAD"),
        },
        "config": {
            "path": config_path.name,
            "sha256": sha256_file(config_path),
        },
        "feeds": feed_provenance(source_root),
        "patches": hashed_files(patch_root),
        "patch_application": patch_report,
        "artifacts": hashed_files(artifact_root) if artifact_root else [],
        "workflow": {
            "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
            "commit": os.environ.get("GITHUB_SHA", "local"),
            "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "local"),
        },
    }
    write_json(REPO_ROOT / args.output, payload)
    print(REPO_ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
