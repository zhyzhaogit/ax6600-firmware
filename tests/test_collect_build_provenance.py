from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import collect_build_provenance  # noqa: E402


class CollectBuildProvenanceTests(unittest.TestCase):
    def test_patch_application_report_is_embedded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "source").mkdir()
            (root / "final.config").write_text("CONFIG_TEST=y\n", encoding="utf-8")
            patch_report = {
                "status": "success",
                "patches": [{"path": "packages/demo/fix.patch", "status": "applied"}],
            }
            (root / "patch-report.json").write_text(json.dumps(patch_report), encoding="utf-8")
            argv = [
                "collect_build_provenance.py",
                "--source-root",
                str(root / "source"),
                "--source-repo",
                "owner/source",
                "--source-branch",
                "stable",
                "--source-ref",
                "a" * 40,
                "--config",
                str(root / "final.config"),
                "--patch-report",
                "patch-report.json",
                "--output",
                "provenance.json",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(collect_build_provenance, "REPO_ROOT", root),
                patch.object(collect_build_provenance, "git_value", return_value="a" * 40),
                patch.object(collect_build_provenance, "feed_provenance", return_value=[]),
                patch.object(collect_build_provenance, "hashed_files", return_value=[]),
            ):
                result = collect_build_provenance.main()

            payload = json.loads((root / "provenance.json").read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(payload["patch_application"], patch_report)


if __name__ == "__main__":
    unittest.main()
