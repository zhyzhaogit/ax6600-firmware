from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import REPO_ROOT, load_yaml, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render runtime uci-defaults overlays from the AX6600 control plane."
    )
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument("--feeds", default="feeds/custom.conf")
    parser.add_argument(
        "--output",
        default="build/ax6600/runtime-overlay/etc/uci-defaults/99-ax6600-defaults",
    )
    return parser.parse_args()


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def custom_feed_names(path: Path) -> list[str]:
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 3 or parts[0] != "src-git":
            raise ValueError(f"unsupported custom feed declaration: {line}")
        name = parts[1]
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", name):
            raise ValueError(f"invalid custom feed name: {name!r}")
        names.append(name)
    return names


def main() -> int:
    args = parse_args()
    manifest = load_yaml(REPO_ROOT / args.manifest)
    defaults = manifest["network_defaults"]
    local_only_feeds = custom_feed_names(REPO_ROOT / args.feeds)

    lan_ip = shell_quote(defaults["lan_ip"])
    ssid = shell_quote(defaults["ssid"])
    theme_path = shell_quote(f"/luci-static/{defaults['theme']}")
    luci_lang = shell_quote(defaults.get("luci_lang", "zh_cn"))
    feed_list = shell_quote(" ".join(local_only_feeds))

    script = "\n".join(
        [
            "#!/bin/sh",
            "set -eu",
            "",
            f"LAN_IP={lan_ip}",
            f"SSID={ssid}",
            f"THEME_PATH={theme_path}",
            f"LUCI_LANG={luci_lang}",
            f"LOCAL_ONLY_FEEDS={feed_list}",
            "",
            "uci -q set network.lan.ipaddr=\"$LAN_IP\"",
            "uci -q commit network",
            "",
            "uci -q set luci.main.mediaurlbase=\"$THEME_PATH\"",
            "uci -q set luci.main.lang=\"$LUCI_LANG\"",
            "uci -q commit luci",
            "",
            "for section in $(uci show wireless 2>/dev/null | sed -n \"s/^wireless\\.\\([^=]*\\)=wifi-iface$/\\1/p\"); do",
            "  uci -q set \"wireless.${section}.ssid=${SSID}\"",
            "done",
            "uci -q commit wireless",
            "",
            "# Custom feeds are compiled into the image and do not publish compatible",
            "# remote APK indexes. Disable their generated repository entries on first boot.",
            "for repo_file in /etc/apk/repositories /etc/apk/repositories.d/distfeeds.list; do",
            "  [ -f \"${repo_file}\" ] || continue",
            "  for feed in ${LOCAL_ONLY_FEEDS}; do",
            "    sed -i \"\\|/${feed}/packages\\.adb$| { /^[[:space:]]*#/! s|^|# |; }\" \"${repo_file}\"",
            "  done",
            "done",
            "",
            "rm -f /etc/uci-defaults/99-ax6600-defaults",
            "",
        ]
    )

    output = REPO_ROOT / args.output
    write_text(output, script)
    output.chmod(0o755)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
