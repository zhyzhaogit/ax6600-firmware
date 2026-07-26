from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import render_runtime_defaults  # noqa: E402


class RuntimeDefaultsTests(unittest.TestCase):
    def test_custom_feeds_are_embedded_in_first_boot_repository_policy(self) -> None:
        manifest = {
            "network_defaults": {
                "lan_ip": "10.0.0.1",
                "ssid": "AX6600",
                "theme": "argon",
                "luci_lang": "zh_cn",
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "feeds.conf").write_text(
                "src-git openclash https://example.invalid/openclash.git;main\n"
                "src-git passwall https://example.invalid/passwall.git;main\n",
                encoding="utf-8",
            )
            argv = [
                "render_runtime_defaults.py",
                "--feeds",
                "feeds.conf",
                "--output",
                "runtime-defaults",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(render_runtime_defaults, "REPO_ROOT", root),
                patch.object(render_runtime_defaults, "load_yaml", return_value=manifest),
            ):
                result = render_runtime_defaults.main()

            rendered = (root / "runtime-defaults").read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertIn("LOCAL_ONLY_FEEDS='openclash passwall'", rendered)
        self.assertIn("/etc/apk/repositories.d/distfeeds.list", rendered)


if __name__ == "__main__":
    unittest.main()
