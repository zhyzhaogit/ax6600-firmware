# Final Package List

This is the current "compile it in by default" package direction for AX6600 / RE-CS-02.

## Built In By The Device Target

- `luci-app-athena-led`
- `luci-i18n-athena-led-zh-cn`

These are already referenced by the `jdcloud_re-cs-02` device definition in the selected upstream.

## Default Enabled Profiles

- `memory-boost`
- `services`
- `proxy-stack`
- `connectivity`
- `storage-nas`
- `usb-network`
- `docker`

## Final Default Package Set

### Access / Localization

- `ca-bundle`
- `ca-certificates`
- `wget-ssl`
- `luci-i18n-base-zh-cn`
- `luci-i18n-firewall-zh-cn`
- `luci-i18n-ddns-go-zh-cn`
- `luci-i18n-autoreboot-zh-cn`
- `luci-i18n-smartdns-zh-cn`
- `luci-i18n-mosdns-zh-cn`
- `luci-i18n-passwall-zh-cn`
- `luci-i18n-zerotier-zh-cn`
- `luci-i18n-easytier-zh-cn`
- `luci-i18n-lucky-zh-cn`
- `luci-i18n-diskman-zh-cn`
- `luci-i18n-dockerman-zh-cn`
- `luci-i18n-netdata-zh-cn`
- `luci-i18n-samba4-zh-cn`
- `luci-i18n-statistics-zh-cn`
- `luci-i18n-ttyd-zh-cn`
- `luci-i18n-upnp-zh-cn`
- `luci-i18n-wol-zh-cn`

### Memory And Device

- `zram-swap`
- `luci-app-athena-led`
- `luci-theme-argon`

### DNS / Daily Services

- `smartdns`
- `luci-app-smartdns`
- `mosdns`
- `luci-app-mosdns`
- `v2dat`
- `adguardhome`
- `luci-app-adguardhome`
- `ddns-go`
- `luci-app-ddns-go`
- `luci-app-autoreboot`
- `ttyd`
- `luci-app-ttyd`
- `luci-app-upnp`
- `luci-app-wol`
- `lucky`
- `luci-app-lucky`

### Observability / Package Management

- `netdata`
- `luci-app-netdata`
- `luci-app-statistics`

### Proxy Stack

- `luci-app-openclash`
- `luci-app-passwall`
- PassWall runtime markers:
  - `CONFIG_PACKAGE_luci-app-passwall_Nftables_Transparent_Proxy=y`
  - `CONFIG_PACKAGE_luci-app-passwall_INCLUDE_SingBox=y`
  - `CONFIG_PACKAGE_luci-app-passwall_INCLUDE_Xray=y`
  - `CONFIG_PACKAGE_luci-app-passwall_INCLUDE_V2ray_Geodata=y`
- Shared proxy support:
  - `kmod-nft-tproxy`

### Remote Connectivity

- `easytier`
- `luci-app-easytier`
- `zerotier`
- `luci-app-zerotier`

### Storage / NAS

- `block-mount`
- `kmod-usb3`
- `kmod-usb-storage`
- `kmod-usb-storage-uas`
- `kmod-fs-ext4`
- `kmod-fs-exfat`
- `kmod-fs-ntfs3`
- `e2fsprogs`
- `parted`
- `smartmontools`
- `blkid`
- `mdadm`
- `btrfs-progs`
- `util-linux`
- `luci-app-diskman`
- `samba4-server`
- `luci-app-samba4`

### USB Network Adapters

- `kmod-usb-net`
- `kmod-usb-net-rtl8152`
- `kmod-usb-net-asix-ax88179`
- `kmod-usb-net-cdc-ether`
- `kmod-usb-net-cdc-ncm`

### Docker

- `containerd`
- `runc`
- `docker`
- `dockerd`
- `docker-compose`
- `luci-lib-docker`
- `luci-app-dockerman`

## Notes

- This list is intentionally aggressive because the target device has relatively usable storage and the user wants future-heavy features compiled in.
- Availability was cross-checked against the current upstream device tree, official ImmortalWrt feeds, and the referenced custom package repositories.
- Runtime enablement is still separate from compile-time inclusion. For example, Samba, ksmbd, Docker, and proxy tools can all be compiled in without forcing all services to start by default.
- Custom-feed packages are compiled into the image. Their remote APK repository entries are disabled in the generated image unless a real public `packages.adb` index exists.
