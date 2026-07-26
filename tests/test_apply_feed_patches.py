from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_feed_patches  # noqa: E402


class ApplyFeedPatchesReportTests(unittest.TestCase):
    def run_tool(self, root: Path, patch_root: Path) -> tuple[int, dict]:
        argv = [
            "apply_feed_patches.py",
            "--source-root",
            str(root / "source"),
            "--patch-root",
            str(patch_root),
            "--report",
            str(root / "patches.md"),
            "--json-report",
            str(root / "patches.json"),
        ]
        with patch.object(sys, "argv", argv):
            result = apply_feed_patches.main()
        payload = json.loads((root / "patches.json").read_text(encoding="utf-8"))
        return result, payload

    def test_empty_patch_set_writes_successful_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            patch_root = root / "patch-root"
            patch_root.mkdir()

            result, payload = self.run_tool(root, patch_root)

        self.assertEqual(result, 0)
        self.assertEqual(payload, {"patches": [], "status": "success"})

    def test_invalid_patch_layout_is_recorded_as_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            patch_root = root / "patch-root"
            patch_root.mkdir()
            (patch_root / "orphan.patch").write_text("not a patch\n", encoding="utf-8")

            result, payload = self.run_tool(root, patch_root)

        self.assertEqual(result, 1)
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["patches"][0]["path"], "orphan.patch")


if __name__ == "__main__":
    unittest.main()
