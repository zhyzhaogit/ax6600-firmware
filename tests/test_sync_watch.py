from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sync_watch  # noqa: E402


class SyncWatchDegradedRunTests(unittest.TestCase):
    def test_fetch_error_is_structured_and_returns_nonzero(self) -> None:
        upstreams = {
            "repositories": {
                "source": {
                    "repo": "owner/source",
                    "branch": "main",
                    "enabled": True,
                }
            }
        }
        compat = {
            "reference_state": {
                "source": {"last_observed_commit": "a" * 40},
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            argv = [
                "sync_watch.py",
                "--output",
                "report.md",
                "--json-output",
                "report.json",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(sync_watch, "REPO_ROOT", root),
                patch.object(sync_watch, "load_yaml", side_effect=[upstreams, compat]),
                patch.object(sync_watch, "github_commit", side_effect=RuntimeError("offline")),
            ):
                result = sync_watch.main()

            payload = json.loads((root / "report.json").read_text(encoding="utf-8"))
            report = (root / "report.md").read_text(encoding="utf-8")

        self.assertEqual(result, 1)
        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["fetch_errors"][0]["key"], "source")
        self.assertIn("degraded", report.lower())


if __name__ == "__main__":
    unittest.main()
