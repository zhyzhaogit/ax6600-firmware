from __future__ import annotations

import argparse
import json

from common import REPO_ROOT, load_yaml


VALID_RUNTIME_STATUSES = {"pass", "passed", "success", "validated"}


def validated_runtime_evidence(entry: dict, metadata: dict) -> tuple[bool, str]:
    evidence = entry.get("runtime_validation_evidence")
    if not isinstance(evidence, dict):
        return False, "runtime validation evidence is missing"

    provenance = metadata.get("provenance")
    if not isinstance(provenance, dict):
        return False, "build provenance is missing from release metadata"

    expected_config = str(evidence.get("config_sha256", "")).lower()
    actual_config = str(provenance.get("config", {}).get("sha256", "")).lower()
    if not expected_config or expected_config != actual_config:
        return False, "validated config SHA256 does not match this build"

    artifact_values = evidence.get("artifact_sha256s", [])
    if not isinstance(artifact_values, list):
        return False, "runtime artifact SHA256 evidence is not a list"
    expected_artifacts = {str(value).lower() for value in artifact_values if value}
    actual_artifacts = {
        str(item.get("sha256", "")).lower()
        for item in provenance.get("artifacts", [])
        if isinstance(item, dict) and item.get("sha256")
    }
    if not expected_artifacts:
        return False, "runtime validation evidence has no artifact SHA256"
    if not expected_artifacts.issubset(actual_artifacts):
        return False, "validated artifact SHA256 does not match this build"
    if not str(evidence.get("report", "")).strip():
        return False, "runtime qualification report is missing"

    return True, "runtime evidence matches build provenance"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce build/runtime policy before publishing AX6600 releases.")
    parser.add_argument("--baseline", default="benchmarks/baseline.yml")
    parser.add_argument("--compat", default="targets/ax6600/compat-matrix.yml")
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--prerelease", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline = load_yaml(REPO_ROOT / args.baseline)
    compat = load_yaml(REPO_ROOT / args.compat)
    metadata = json.loads((REPO_ROOT / args.metadata).read_text(encoding="utf-8"))
    policy = baseline.get("validation_policy", {})

    source = metadata["source"]
    matching = [
        entry
        for entry in compat.get("known_good", [])
        if entry.get("source_repo") == source.get("repo") and entry.get("source_commit") == source.get("commit")
    ]
    if not matching:
        print(f"Source {source.get('repo')}@{source.get('commit')} is not recorded as known-good.")
        return 1

    entry = matching[0]
    if entry.get("build_status") != "success":
        print(f"Known-good entry has non-success build status: {entry.get('build_status')}")
        return 1

    runtime_status = str(entry.get("runtime_validation_status", "pending")).lower()
    if runtime_status in VALID_RUNTIME_STATUSES:
        evidence_valid, reason = validated_runtime_evidence(entry, metadata)
        if evidence_valid:
            print(reason)
            return 0
        print(f"Runtime status is {runtime_status!r}, but {reason}.")
        return 1
    if args.prerelease and policy.get("allow_prerelease_with_pending_runtime_checks", False):
        print(f"Prerelease allowed with runtime status {runtime_status!r}.")
        return 0
    if policy.get("allow_release_with_pending_runtime_checks", False):
        print(f"Release allowed by policy with runtime status {runtime_status!r}.")
        return 0

    print(f"Stable release blocked: runtime validation status is {runtime_status!r}.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
