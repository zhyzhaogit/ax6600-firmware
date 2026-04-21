from __future__ import annotations

import argparse
from pathlib import Path

from common import REPO_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply package enable/disable overrides to a generated config.")
    parser.add_argument("--config", required=True, help="Config file path relative to repo root")
    parser.add_argument(
        "--overrides",
        default="",
        help="Whitespace, comma, or newline separated package overrides. Use -pkg to disable.",
    )
    return parser.parse_args()


def normalize_overrides(raw: str) -> list[tuple[str, str]]:
    tokens = []
    for chunk in raw.replace(",", "\n").splitlines():
        for token in chunk.split():
            cleaned = token.strip()
            if cleaned:
                tokens.append(cleaned)

    normalized: list[tuple[str, str]] = []
    for token in tokens:
        mode = "enable"
        name = token
        if token[0] in {"+", "-","!"}:
            name = token[1:]
            mode = "disable" if token[0] in {"-", "!"} else "enable"
        if not name:
            continue
        normalized.append((mode, name))
    return normalized


def main() -> int:
    args = parse_args()
    config_path = REPO_ROOT / args.config
    lines = config_path.read_text(encoding="utf-8").splitlines()

    overrides = normalize_overrides(args.overrides)
    if not overrides:
        return 0

    package_names = {name for _, name in overrides}
    filtered_lines = [
        line
        for line in lines
        if not any(
            line.startswith(f"CONFIG_PACKAGE_{name}=") or line == f"# CONFIG_PACKAGE_{name} is not set"
            for name in package_names
        )
    ]

    filtered_lines.append("")
    filtered_lines.append("# --- begin package overrides ---")
    for mode, name in overrides:
        if mode == "enable":
            filtered_lines.append(f"CONFIG_PACKAGE_{name}=y")
        else:
            filtered_lines.append(f"# CONFIG_PACKAGE_{name} is not set")
    filtered_lines.append("# --- end package overrides ---")
    filtered_lines.append("")

    config_path.write_text("\n".join(filtered_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
