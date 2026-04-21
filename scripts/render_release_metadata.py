from __future__ import annotations

import argparse
from datetime import datetime, timezone

from common import REPO_ROOT, load_yaml, write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render release metadata from the control plane.")
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument("--compat", default="targets/ax6600/compat-matrix.yml")
    parser.add_argument("--policy", default="targets/ax6600/feature-policy.yml")
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--optional-profiles", default="")
    parser.add_argument(
        "--replace-default-optional-profiles",
        action="store_true",
        help="Do not include manifest release.default_optional_profiles in the reported profile set.",
    )
    parser.add_argument("--patch-set-version", default="firmware-layer-v1")
    parser.add_argument("--output-json", default="dist/release/release-metadata.json")
    parser.add_argument("--output-md", default="dist/release/release-metadata.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_yaml(REPO_ROOT / args.manifest)
    compat = load_yaml(REPO_ROOT / args.compat)
    policy = load_yaml(REPO_ROOT / args.policy)
    selected_profiles = [item.strip() for item in args.optional_profiles.split(",") if item.strip()]
    default_profiles = [] if args.replace_default_optional_profiles else list(
        manifest.get("release", {}).get("default_optional_profiles", [])
    )
    merged_profiles = list(default_profiles)
    for item in selected_profiles:
        if item not in merged_profiles:
            merged_profiles.append(item)

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": manifest["target"],
        "device": manifest["device"]["marketing_name"],
        "source": {
            "repo": args.source_repo,
            "branch": args.source_branch,
            "commit": args.source_commit,
        },
        "release": manifest["release"],
        "network_defaults": manifest["network_defaults"],
        "config_profile": manifest["device"]["config_profile"],
        "optional_profiles": merged_profiles,
        "patch_set_version": args.patch_set_version,
        "required_features": sorted(
            name for name, feature in policy["features"].items() if feature["level"] == "required"
        ),
        "known_good_reference": compat["known_good"][0]["id"],
    }

    markdown = "\n".join(
        [
            "# Release Metadata",
            "",
            f"- target: `{metadata['target']}`",
            f"- device: `{metadata['device']}`",
            f"- source: `{args.source_repo}` @ `{args.source_branch}`",
            f"- source commit: `{args.source_commit}`",
            f"- config profile: `{metadata['config_profile']}`",
            f"- optional profiles: `{', '.join(merged_profiles) if merged_profiles else 'none'}`",
            f"- patch set version: `{args.patch_set_version}`",
            f"- known-good reference: `{metadata['known_good_reference']}`",
            "",
        ]
    )

    write_json(REPO_ROOT / args.output_json, metadata)
    write_text(REPO_ROOT / args.output_md, markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
