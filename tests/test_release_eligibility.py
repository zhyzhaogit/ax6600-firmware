from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_release_eligibility  # noqa: E402


class ReleaseEligibilityTests(unittest.TestCase):
    def run_check(
        self,
        prerelease: bool,
        runtime_status: str = "pending",
        evidence: dict | None = None,
        config_sha256: str = "b" * 64,
        artifact_sha256: str = "c" * 64,
    ) -> int:
        baseline = {
            "validation_policy": {
                "allow_release_with_pending_runtime_checks": False,
                "allow_prerelease_with_pending_runtime_checks": True,
            }
        }
        compat = {
            "known_good": [
                {
                    "source_repo": "owner/source",
                    "source_commit": "a" * 40,
                    "build_status": "success",
                    "runtime_validation_status": runtime_status,
                    **({"runtime_validation_evidence": evidence} if evidence is not None else {}),
                }
            ]
        }
        metadata = {
            "source": {"repo": "owner/source", "commit": "a" * 40},
            "provenance": {
                "config": {"sha256": config_sha256},
                "artifacts": [{"path": "sysupgrade.bin", "sha256": artifact_sha256}],
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            argv = ["check_release_eligibility.py", "--metadata", "metadata.json"]
            if prerelease:
                argv.append("--prerelease")
            with (
                patch.object(sys, "argv", argv),
                patch.object(check_release_eligibility, "REPO_ROOT", root),
                patch.object(check_release_eligibility, "load_yaml", side_effect=[baseline, compat]),
            ):
                return check_release_eligibility.main()

    def test_pending_runtime_blocks_stable_release(self) -> None:
        self.assertEqual(self.run_check(prerelease=False), 1)

    def test_pending_runtime_allows_prerelease_when_policy_allows(self) -> None:
        self.assertEqual(self.run_check(prerelease=True), 0)

    def test_validated_runtime_requires_hash_evidence(self) -> None:
        self.assertEqual(self.run_check(prerelease=False, runtime_status="passed"), 1)

    def test_validated_runtime_accepts_matching_build_evidence(self) -> None:
        evidence = {
            "config_sha256": "b" * 64,
            "artifact_sha256s": ["c" * 64],
            "report": "reports/router-qualification.md",
        }
        self.assertEqual(
            self.run_check(prerelease=False, runtime_status="passed", evidence=evidence),
            0,
        )

    def test_validated_runtime_rejects_different_artifact(self) -> None:
        evidence = {
            "config_sha256": "b" * 64,
            "artifact_sha256s": ["d" * 64],
            "report": "reports/router-qualification.md",
        }
        self.assertEqual(
            self.run_check(prerelease=False, runtime_status="passed", evidence=evidence),
            1,
        )

    def test_validated_runtime_requires_qualification_report(self) -> None:
        evidence = {"config_sha256": "b" * 64, "artifact_sha256s": ["c" * 64]}
        self.assertEqual(
            self.run_check(prerelease=False, runtime_status="passed", evidence=evidence),
            1,
        )


if __name__ == "__main__":
    unittest.main()
