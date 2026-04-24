from __future__ import annotations

import argparse
from pathlib import Path

from common import REPO_ROOT, load_yaml, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render runtime uci-defaults overlays from the AX6600 control plane."
    )
    parser.add_argument("--manifest", default="targets/ax6600/manifest.yml")
    parser.add_argument(
        "--output",
        default="build/ax6600/runtime-overlay/etc/uci-defaults/99-ax6600-defaults",
    )
    return parser.parse_args()


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main() -> int:
    args = parse_args()
    manifest = load_yaml(REPO_ROOT / args.manifest)
    defaults = manifest["network_defaults"]

    lan_ip = shell_quote(defaults["lan_ip"])
    ssid = shell_quote(defaults["ssid"])
    theme_path = shell_quote(f"/luci-static/{defaults['theme']}")
    luci_lang = shell_quote(defaults.get("luci_lang", "zh_cn"))

    script = "\n".join(
        [
            "#!/bin/sh",
            "set -eu",
            "",
            f"LAN_IP={lan_ip}",
            f"SSID={ssid}",
            f"THEME_PATH={theme_path}",
            f"LUCI_LANG={luci_lang}",
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
