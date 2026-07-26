from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import render_release_metadata  # noqa: E402


def fixture_documents() -> list[dict]:
    manifest = {
        "target": "ax6600",
        "device": {
            "marketing_name": "AX6600",
            "config_profile": "IPQ60XX-WIFI-YES",
            "openwrt_target": "qualcommax/ipq60xx",
        },
        "release": {
            "default_optional_profiles": ["services"],
            "timezone": "UTC",
        },
        "network_defaults": {
            "lan_ip": "10.0.0.1",
            "ssid": "AX6600",
            "wifi_password_hint": "set-after-flash",
        },
        "config_fragments": {"optional_profiles": {"services": "services.config"}},
    }
    compat = {"known_good": [{"id": "known-good"}]}
    policy = {"features": {"release_transparency": {"level": "required"}}}
    package_plan = {
        "built_in_target_packages": [],
        "profiles": {"services": {"packages": ["luci"]}},
    }
    return [manifest, compat, policy, package_plan]


class ReleaseMetadataValidationTests(unittest.TestCase):
    def test_supplied_provenance_is_nested_in_metadata(self) -> None:
        provenance = {
            "workflow": "build-ax6600",
            "run_id": "12345",
            "artifact": "firmware-image",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
            argv = [
                "render_release_metadata.py",
                "--source-repo",
                "owner/source",
                "--source-branch",
                "main",
                "--source-commit",
                "a" * 40,
                "--provenance",
                "provenance.json",
                "--output-json",
                "metadata.json",
                "--output-md",
                "metadata.md",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(render_release_metadata, "REPO_ROOT", root),
                patch.object(render_release_metadata, "load_yaml", side_effect=fixture_documents()),
            ):
                result = render_release_metadata.main()

            metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(metadata["provenance"], provenance)

    def test_unknown_selected_profile_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            argv = [
                "render_release_metadata.py",
                "--source-repo",
                "owner/source",
                "--source-branch",
                "main",
                "--source-commit",
                "a" * 40,
                "--optional-profiles",
                "missing-profile",
                "--output-json",
                "metadata.json",
                "--output-md",
                "metadata.md",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(render_release_metadata, "REPO_ROOT", root),
                patch.object(render_release_metadata, "load_yaml", side_effect=fixture_documents()),
            ):
                with self.assertRaisesRegex(SystemExit, "Unknown optional profile"):
                    render_release_metadata.main()

            self.assertFalse((root / "metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
