from __future__ import annotations

import argparse
import re
from pathlib import Path


TARGETS = (
    "feeds/dockerman/applications/luci-app-dockerman/Makefile",
    "feeds/luci_lib_docker/collections/luci-lib-docker/Makefile",
)

VERSION_RE = re.compile(r"^(\ufeff?PKG_VERSION:=)v(\d.*)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize APK-incompatible feed package versions after feeds are installed."
    )
    parser.add_argument("--source-root", default="work/source")
    return parser.parse_args()


def normalize_makefile(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    updated = VERSION_RE.sub(r"\1\2", original)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root)
    changed: list[Path] = []
    for rel_path in TARGETS:
        path = source_root / rel_path
        if normalize_makefile(path):
            changed.append(path)

    if changed:
        print("Normalized APK package versions:")
        for path in changed:
            print(path)
    else:
        print("No APK feed version normalization needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
