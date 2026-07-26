from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import resolve_source  # noqa: E402


class ResolveSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = {"source_selection": {"bootstrap_upstream": "primary"}}
        self.upstreams = {
            "repositories": {
                "primary": {
                    "repo": "owner/source",
                    "branch": "stable",
                    "enabled": True,
                }
            }
        }

    def test_exact_ref_overrides_configured_branch(self) -> None:
        result = resolve_source.resolve_source(self.manifest, self.upstreams, "primary", "a" * 40)

        self.assertEqual(result["SOURCE_BRANCH"], "stable")
        self.assertEqual(result["SOURCE_REF"], "a" * 40)

    def test_unknown_source_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown source key"):
            resolve_source.resolve_source(self.manifest, self.upstreams, "missing", "")

    def test_unsafe_ref_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid source ref"):
            resolve_source.resolve_source(self.manifest, self.upstreams, "primary", "main;echo-bad")


if __name__ == "__main__":
    unittest.main()
