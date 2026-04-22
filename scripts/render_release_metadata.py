from __future__ import annotations

import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from common import REPO_ROOT, load_yaml, write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render release metadata from the control plane.")
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument("--compat", default="targets/ax6600/compat-matrix.yml")
    parser.add_argument("--policy", default="targets/ax6600/feature-policy.yml")
    parser.add_argument("--package-plan", default="targets/ax6600/package-plan.yml")
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
    package_plan = load_yaml(REPO_ROOT / args.package_plan)
    selected_profiles = [item.strip() for item in args.optional_profiles.split(",") if item.strip()]
    default_profiles = [] if args.replace_default_optional_profiles else list(
        manifest.get("release", {}).get("default_optional_profiles", [])
    )
    merged_profiles = list(default_profiles)
    for item in selected_profiles:
        if item not in merged_profiles:
            merged_profiles.append(item)

    tz_name = manifest.get("release", {}).get("timezone", "UTC")
    local_generated_at = datetime.now(ZoneInfo(tz_name)).isoformat()
    source_commit_short = args.source_commit[:7]
    built_in_packages = list(package_plan.get("built_in_target_packages", []))
    enabled_profile_packages: list[str] = []
    for profile_name in merged_profiles:
        profile = package_plan.get("profiles", {}).get(profile_name, {})
        for package in profile.get("packages", []):
            if package not in enabled_profile_packages:
                enabled_profile_packages.append(package)

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_at_local": local_generated_at,
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
        "built_in_target_packages": built_in_packages,
        "enabled_profile_packages": enabled_profile_packages,
        "patch_set_version": args.patch_set_version,
        "required_features": sorted(
            name for name, feature in policy["features"].items() if feature["level"] == "required"
        ),
        "known_good_reference": compat["known_good"][0]["id"],
    }

    profile_label = ", ".join(merged_profiles) if merged_profiles else "none"
    package_lines = [
        f"- target built-ins: {', '.join(built_in_packages) if built_in_packages else 'none'}",
        f"- enabled profile packages: {', '.join(enabled_profile_packages) if enabled_profile_packages else 'none'}",
    ]

    markdown = "\n".join(
        [
            "OpenWrt Build for AX6600 / IPQ6010",
            "",
            "-----------------------",
            "",
            "Basic Information",
            f"Source repository: https://github.com/{args.source_repo}.git",
            f"Build branch: {args.source_branch}",
            f"Commit version: {source_commit_short}",
            f"Build time: {local_generated_at}",
            "",
            "-----------------------",
            "",
            "Device And Platform",
            f"Device model: {metadata['device']}",
            f"Hardware target: {manifest['device']['openwrt_target']}",
            "CPU architecture: Qualcomm IPQ6010 / IPQ60xx",
            "",
            "-----------------------",
            "",
            "Firmware Highlights",
            "",
            "NSS hardware acceleration support",
            "Built through the OpenWrt / ImmortalWrt control plane",
            "Common LuCI packages pre-integrated",
            "Cloud build automation enabled",
            "Supports config fragments and package override builds",
            "",
            "-----------------------",
            "",
            "Default Access",
            f"LAN address: {manifest['network_defaults']['lan_ip']}",
            "Admin password: none",
            "",
            f"WiFi name: {manifest['network_defaults']['ssid']}",
            f"WiFi password: {manifest['network_defaults']['wifi_password_hint']}",
            "",
            "-----------------------",
            "",
            "Usage Notes",
            "",
            "Choose the firmware file that matches the target device.",
            "Use factory for first flash and sysupgrade for upgrades from OpenWrt.",
            "",
            "Risk Reminder",
            "Flashing has risk. Confirm these points before you proceed:",
            "",
            "Original firmware backup is available",
            "U-Boot or TTL recovery is available",
            "Partition layout is understood",
            "",
            "-----------------------",
            "",
            "Build Details",
            f"Config profile: {metadata['config_profile']}",
            f"Enabled profiles: {profile_label}",
            f"Patch set version: {args.patch_set_version}",
            f"Compatibility baseline: {metadata['known_good_reference']}",
            f"Required features: {', '.join(metadata['required_features'])}",
            "",
            "Selected Package Summary",
            *package_lines,
            "",
        ]
    )

    write_json(REPO_ROOT / args.output_json, metadata)
    write_text(REPO_ROOT / args.output_md, markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
