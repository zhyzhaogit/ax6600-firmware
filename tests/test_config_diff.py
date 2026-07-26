from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import config_diff  # noqa: E402


class ConfigDiffPersistentStateTests(unittest.TestCase):
    def test_fetch_error_preserves_last_successful_state_and_degrades_run(self) -> None:
        upstreams = {
            "policy": {
                "protected_keywords": [],
                "default_compare_targets": ["reference"],
            },
            "repositories": {
                "reference": {
                    "repo": "owner/repo",
                    "branch": "main",
                    "watched_paths": ["Config/device.txt"],
                }
            },
        }
        previous_entry = {"sha256": "known-good-digest", "category": "config-absorb"}

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = root / "state.json"
            state_path.write_text(
                json.dumps({"reference": {"Config/device.txt": previous_entry}}),
                encoding="utf-8",
            )
            argv = [
                "config_diff.py",
                "--state",
                "state.json",
                "--output",
                "report.md",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(config_diff, "REPO_ROOT", root),
                patch.object(config_diff, "load_yaml", return_value=upstreams),
                patch.object(config_diff, "github_raw", side_effect=RuntimeError("offline")),
            ):
                result = config_diff.main()

            persisted = json.loads(state_path.read_text(encoding="utf-8"))
            report = (root / "report.md").read_text(encoding="utf-8")

        self.assertEqual(result, 1)
        self.assertEqual(persisted["reference"]["Config/device.txt"], previous_entry)
        self.assertIn("degraded", report.lower())


if __name__ == "__main__":
    unittest.main()
