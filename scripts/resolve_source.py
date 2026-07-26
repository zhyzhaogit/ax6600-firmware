from __future__ import annotations

import argparse
import re

from common import REPO_ROOT, load_yaml, write_text


REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve and validate an AX6600 source repository/ref.")
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument("--upstreams", default="targets/ax6600/upstreams.yml")
    parser.add_argument("--source-key", default="")
    parser.add_argument("--source-ref", default="")
    parser.add_argument("--output", default="source.env")
    return parser.parse_args()


def validate_ref(value: str) -> str:
    if not REF_RE.fullmatch(value) or ".." in value or "@{" in value or value.endswith("."):
        raise ValueError(f"invalid source ref: {value!r}")
    return value


def resolve_source(manifest: dict, upstreams: dict, source_key: str, source_ref: str) -> dict[str, str]:
    requested = source_key.strip() or manifest["source_selection"]["bootstrap_upstream"]
    repositories = upstreams["repositories"]
    if requested not in repositories:
        raise ValueError(f"unknown source key: {requested}")

    entry = repositories[requested]
    if not entry.get("enabled", False):
        raise ValueError(f"source key is disabled: {requested}")

    repository = str(entry["repo"])
    if not REPOSITORY_RE.fullmatch(repository):
        raise ValueError(f"invalid source repository: {repository!r}")

    configured_branch = validate_ref(str(entry["branch"]))
    resolved_ref = validate_ref(source_ref.strip() or configured_branch)
    return {
        "SOURCE_KEY": requested,
        "SOURCE_REPO": repository,
        "SOURCE_BRANCH": configured_branch,
        "SOURCE_REF": resolved_ref,
    }


def main() -> int:
    args = parse_args()
    manifest = load_yaml(REPO_ROOT / args.manifest)
    upstreams = load_yaml(REPO_ROOT / args.upstreams)
    try:
        source = resolve_source(manifest, upstreams, args.source_key, args.source_ref)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    content = "".join(f"{key}={value}\n" for key, value in source.items())
    write_text(REPO_ROOT / args.output, content)
    print(f"resolved {source['SOURCE_KEY']} -> {source['SOURCE_REPO']}@{source['SOURCE_REF']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
