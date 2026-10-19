from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_feed_patches  # noqa: E402


@unittest.skipUnless(shutil.which("patch"), "GNU patch is required")
class PatchApplicationTests(unittest.TestCase):
    def test_patch_with_deleted_file_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            obsolete = root / "obsolete.patch"
            obsolete.write_text("old fix\n", encoding="utf-8")
            target = root / "logging.patch"
            target.write_text("old context\n", encoding="utf-8")
            patch_file = root / "refresh.patch"
            patch_file.write_text(
                "--- a/obsolete.patch\n+++ /dev/null\n@@ -1 +0,0 @@\n-old fix\n"
                "--- a/logging.patch\n+++ b/logging.patch\n@@ -1 +1 @@\n-old context\n+new context\n",
                encoding="utf-8",
            )
            self.assertEqual(apply_feed_patches.patch_state(root, patch_file), "applied")
            self.assertFalse(obsolete.exists())
            applied = target.read_bytes()
            self.assertEqual(apply_feed_patches.patch_state(root, patch_file), "already-applied")
            self.assertFalse(obsolete.exists())
            self.assertEqual(target.read_bytes(), applied)

    def test_repeated_application_does_not_revert_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "Makefile"
            target.write_text("before\n", encoding="utf-8")
            patch_file = root / "change.patch"
            patch_file.write_text(
                "--- a/Makefile\n+++ b/Makefile\n@@ -1 +1 @@\n-before\n+after\n",
                encoding="utf-8",
            )
            self.assertEqual(apply_feed_patches.patch_state(root, patch_file), "applied")
            applied = target.read_bytes()
            self.assertEqual(apply_feed_patches.patch_state(root, patch_file), "already-applied")
            self.assertEqual(target.read_bytes(), applied)

    def test_incompatible_patch_fails_without_changing_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "Makefile"
            target.write_text("upstream changed\n", encoding="utf-8")
            patch_file = root / "change.patch"
            patch_file.write_text(
                "--- a/Makefile\n+++ b/Makefile\n@@ -1 +1 @@\n-before\n+after\n",
                encoding="utf-8",
            )
            before = target.read_bytes()
            with self.assertRaises(RuntimeError):
                apply_feed_patches.patch_state(root, patch_file)
            self.assertEqual(target.read_bytes(), before)


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
