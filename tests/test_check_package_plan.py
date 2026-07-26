from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_package_plan  # noqa: E402


class CheckPackagePlanEffectiveSelectionTests(unittest.TestCase):
    def test_parser_accepts_effective_selection_arguments(self) -> None:
        argv = [
            "check_package_plan.py",
            "--optional-profiles",
            "services,docker",
            "--replace-default-optional-profiles",
            "--package-overrides=-dropme,+extra",
        ]

        with patch.object(sys, "argv", argv):
            args = check_package_plan.parse_args()

        self.assertEqual(args.optional_profiles, "services,docker")
        self.assertTrue(args.replace_default_optional_profiles)
        self.assertEqual(args.package_overrides, "-dropme,+extra")

    def test_replacing_defaults_requires_only_selected_profile_packages(self) -> None:
        manifest = {
            "release": {"default_optional_profiles": ["default-profile"]},
            "config_fragments": {
                "optional_profiles": {
                    "default-profile": "default.config",
                    "selected-profile": "selected.config",
                }
            },
        }
        plan = {
            "default_enabled_profiles": ["default-profile"],
            "profiles": {
                "default-profile": {"packages": ["default-package"]},
                "selected-profile": {"packages": ["selected-package"]},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "final.config").write_text("CONFIG_PACKAGE_selected-package=y\n", encoding="utf-8")
            argv = [
                "check_package_plan.py",
                "--config",
                "final.config",
                "--output",
                "report.md",
                "--optional-profiles",
                "selected-profile",
                "--replace-default-optional-profiles",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(check_package_plan, "REPO_ROOT", root),
                patch.object(check_package_plan, "load_yaml", side_effect=[manifest, plan]),
            ):
                result = check_package_plan.main()

        self.assertEqual(result, 0)

    def test_disabled_package_override_is_not_required(self) -> None:
        manifest = {
            "release": {"default_optional_profiles": ["services"]},
            "config_fragments": {"optional_profiles": {"services": "services.config"}},
        }
        plan = {
            "default_enabled_profiles": ["services"],
            "profiles": {"services": {"packages": ["keepme", "dropme"]}},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "final.config").write_text("CONFIG_PACKAGE_keepme=y\n", encoding="utf-8")
            argv = [
                "check_package_plan.py",
                "--config",
                "final.config",
                "--output",
                "report.md",
                "--package-overrides=-dropme",
            ]

            with (
                patch.object(sys, "argv", argv),
                patch.object(check_package_plan, "REPO_ROOT", root),
                patch.object(check_package_plan, "load_yaml", side_effect=[manifest, plan]),
            ):
                result = check_package_plan.main()

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
