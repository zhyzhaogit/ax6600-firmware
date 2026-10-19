# Firmware-Layer Patches

Use this directory for adjustments that should be applied after the source tree is checked out but before build validation:

- package tweaks
- feed-side fixes
- product-level file overrides

Do not place source fork history here. If a change must be carried long-term against upstream source, move it to `ax6600-source`.

## Feed Package Patches

Feed package patches are organized as: `feed-packages/<feed-name>/<package-name>/*.patch`

Example: `feed-packages/packages/netdata/0001-disable-cloud-aclk.patch`

Supported feed names:
- `packages` (immortalwrt/packages)
- `luci` (immortalwrt/luci)
- `routing` (openwrt/routing)
- `telephony` (openwrt/telephony)
- `video` (openwrt/video)

## Active Patches

### miniupnpd

- `0001-refresh-patches-for-2.3.11.patch`: Backport
  [immortalwrt/packages PR #2001](https://github.com/immortalwrt/packages/pull/2001)
  at commit `11ebc02d3914b5b3e05c964ac1d21f7e5b8cd6be` (yuayu).
  - Remove `020-descr-filter-fix.patch` and `030-allow-private-fix.patch` because
    MiniUPnPd 2.3.11 already contains their fixes.
  - Refresh `040-improve-logging.patch`; retain `010` and `900`.
  - Keep MiniUPnPd 2.3.11 and its security fixes instead of downgrading the feed.
  - Once the feed carries this change, the helper must report `already-applied`.
    Recheck or retire this backport if upstream refreshes these files differently;
    incompatible changes must stop preparation rather than be ignored.

### netdata

- `0001-disable-cloud-aclk.patch`: Disable Netdata Cloud (ACLK) to fix protobuf/absl API incompatibility
  - Issue: absl::LogMessageFatal constructor signature changed in newer versions
  - Solution: Disable cloud feature (--disable-cloud) which requires problematic protobuf code
