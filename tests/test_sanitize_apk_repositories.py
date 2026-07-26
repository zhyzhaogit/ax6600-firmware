from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sanitize_apk_repositories  # noqa: E402


class ApkRepositoryClassificationTests(unittest.TestCase):
    def test_allowed_feed_repository_is_kept(self) -> None:
        line = "https://downloads.example/packages/aarch64/packages/packages.adb"

        rewritten, action = sanitize_apk_repositories.classify_line(line, {"packages"})

        self.assertEqual(rewritten, line)
        self.assertEqual(action, "kept")

    def test_custom_feed_repository_is_disabled(self) -> None:
        line = "https://downloads.example/packages/aarch64/custom/packages.adb"

        rewritten, action = sanitize_apk_repositories.classify_line(line, {"packages"})

        self.assertEqual(rewritten, f"# {line}")
        self.assertEqual(action, "disabled:custom")

    def test_non_apk_repository_line_is_unchanged(self) -> None:
        line = "https://downloads.example/releases/targets/qualcommax/ipq60xx"

        rewritten, action = sanitize_apk_repositories.classify_line(line, {"packages"})

        self.assertEqual(rewritten, line)
        self.assertEqual(action, "unchanged")

    def test_commented_repository_line_is_unchanged(self) -> None:
        line = "# https://downloads.example/packages/aarch64/custom/packages.adb"

        rewritten, action = sanitize_apk_repositories.classify_line(line, {"packages"})

        self.assertEqual(rewritten, line)
        self.assertEqual(action, "unchanged")


if __name__ == "__main__":
    unittest.main()
