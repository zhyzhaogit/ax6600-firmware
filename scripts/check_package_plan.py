from __future__ import annotations

import argparse

from common import REPO_ROOT, load_yaml, markdown_table, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate that the assembled config contains the default package plan.")
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument("--package-plan", default="targets/ax6600/package-plan.yml")
    parser.add_argument("--config", default="build/ax6600/.config")
    parser.add_argument("--output", default="reports/package-plan-check.md")
    parser.add_argument(
        "--config-phase",
        choices=("assembled", "final"),
        default="final",
        help="Use 'assembled' for pre-feed baseline configs and 'final' for post-defconfig validation.",
    )
    return parser.parse_args()


def package_to_config_marker(name: str) -> str:
    return f"CONFIG_PACKAGE_{name}=y"


def main() -> int:
    args = parse_args()
    manifest = load_yaml(REPO_ROOT / args.manifest)
    plan = load_yaml(REPO_ROOT / args.package_plan)
    config_text = (REPO_ROOT / args.config).read_text(encoding="utf-8")

    manifest_defaults = manifest.get("release", {}).get("default_optional_profiles", [])
    plan_defaults = plan.get("default_enabled_profiles", [])

    rows: list[list[str]] = []
    failures: list[str] = []

    if manifest_defaults != plan_defaults:
        failures.append("default_enabled_profiles mismatch")
        rows.append(
            [
                "defaults",
                "manifest/package-plan alignment",
                "fail",
                f"manifest={manifest_defaults} plan={plan_defaults}",
            ]
        )
    else:
        rows.append(["defaults", "manifest/package-plan alignment", "pass", ", ".join(manifest_defaults)])

    for profile_name in plan_defaults:
        profile = plan["profiles"][profile_name]
        for package in profile.get("packages", []):
            marker = package_to_config_marker(package)
            status = "pass" if marker in config_text else "fail"
            if status == "fail":
                failures.append(marker)
            rows.append([profile_name, package, status, marker])
        for marker in profile.get("config_markers", []):
            if args.config_phase == "assembled":
                rows.append([profile_name, marker, "skip", "deferred until final config validation"])
                continue
            status = "pass" if marker in config_text else "fail"
            if status == "fail":
                failures.append(marker)
            rows.append([profile_name, marker, status, marker])

    phase_note = (
        "Config markers are skipped in assembled mode because feed-resolved dependency symbols are not stable yet."
        if args.config_phase == "assembled"
        else "Config markers are enforced in final mode after feeds and defconfig have resolved derived symbols."
    )

    report = "\n".join(
        [
            "# Package Plan Check",
            "",
            f"- config phase: `{args.config_phase}`",
            f"- note: {phase_note}",
            "",
            markdown_table(["profile", "item", "status", "evidence"], rows),
            "",
            "Built-in target packages are documented in `targets/ax6600/package-plan.yml` but are not enforced here,",
            "because they come from the selected device definition rather than direct config symbols.",
            "",
        ]
    )
    write_text(REPO_ROOT / args.output, report)

    if failures:
        print("Package plan check failed:")
        for item in failures:
            print(item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
