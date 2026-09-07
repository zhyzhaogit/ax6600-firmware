from __future__ import annotations

import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


class MosdnsGeo2txtMigrationTests(unittest.TestCase):
    def test_active_control_plane_uses_geo2txt(self) -> None:
        services_config = (
            REPO_ROOT / "config/ax6600/40-optional-profiles/services.config"
        ).read_text(encoding="utf-8")
        package_plan = yaml.safe_load(
            (REPO_ROOT / "targets/ax6600/package-plan.yml").read_text(encoding="utf-8")
        )
        preparation_script = (REPO_ROOT / "scripts/prepare_defconfig.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("CONFIG_PACKAGE_geo2txt=y", services_config)
        self.assertNotIn("CONFIG_PACKAGE_v2dat=y", services_config)
        self.assertIn("geo2txt", package_plan["profiles"]["services"]["packages"])
        self.assertNotIn("v2dat", package_plan["profiles"]["services"]["packages"])
        self.assertIn("luci-app-mosdns geo2txt", preparation_script)
        self.assertNotIn("luci-app-mosdns v2dat", preparation_script)


if __name__ == "__main__":
    unittest.main()
