# AX6600 / RE-CS-02 OpenWrt Firmware

面向京东云雅典娜 `RE-CS-02` / `AX6600` 的可持续 OpenWrt / ImmortalWrt 固件项目。

本仓库不是简单复制某个云编译仓库，而是一个“产品层”固件仓库：它把设备配置、包选择、上游来源、发布策略、校验规则和 GitHub Actions 自动构建都固定成机器可读文件，方便长期维护，也方便以后继续用 AI 辅助跟进上游更新。

English documentation is available below.

## 项目状态

- 目标设备：`JDCloud RE-CS-02 / AX6600`
- OpenWrt target：`qualcommax/ipq60xx`
- 默认源码：`zhyzhaogit/ax6600-source@ax6600-stable`
- 固件产物：同时生成 `factory.bin` 和 `sysupgrade.bin`
- 默认 LAN：`10.0.0.1`
- 默认主题：`luci-theme-argon`
- 默认语言：中文优先，语言包按可用性尽量集成
- 包管理：使用新版 `apk` 生态，不混用 `opkg` / iStore

最新固件请到 [Releases](https://github.com/zhyzhaogit/ax6600-firmware/releases) 下载。

## 固件特性

| 能力 | 默认状态 | 说明 |
| --- | --- | --- |
| NSS 硬件加速 | 已启用并校验 | 保留 AX6600 / IPQ60xx 的核心性能优势 |
| 自动云编译 | 已启用 | `main` 成功构建会发布 prerelease |
| 首刷和升级包 | 已生成 | `factory.bin` 用于首刷，`sysupgrade.bin` 用于 OpenWrt 内升级 |
| HTTPS 包管理支持 | 已内置 | 包含 `wget-ssl`、`ca-bundle`、`ca-certificates` |
| 中文界面 | 尽量集成 | i18n 包缺失时只警告，不阻断固件发布 |
| Argon 主题 | 默认启用 | 首次进入 LuCI 即使用 Argon |
| Athena LED | 设备目标内置 | 包含雅典娜 LED 相关 LuCI 支持 |
| Docker / NAS / USB 扩展 | 已编译进固件 | 默认适合后续外接硬盘、容器、USB 网卡扩展 |

## 选择哪个文件刷机

请确认设备型号是 `RE-CS-02` / `AX6600` / `jdcloud_re-cs-02` 后再刷写。

| 文件 | 用途 |
| --- | --- |
| `*-factory.bin` | 从原厂固件、U-Boot Web、救砖环境或非 OpenWrt 系统首次刷入 |
| `*-sysupgrade.bin` | 已经运行 OpenWrt / ImmortalWrt 时，在 LuCI 或命令行里升级 |

刷机有风险。刷写前请确认：

- 已备份原厂固件和重要配置
- 知道如何进入 U-Boot 或 TTL 恢复
- 确认自己的设备分区和型号匹配
- 不要把其他 AX6600 型号的固件混刷到本设备

## 默认内置包

默认固件偏“完整可用”，会把常用功能直接编译进镜像，避免后续因 apk 源变化导致装不上。

主要包括：

- 基础与界面：`luci`、`luci-compat`、`luci-theme-argon`
- 网络与 NSS：NSS 相关配置、`dnsmasq-full`、`irqbalance`、`ethtool`
- HTTPS 与证书：`wget-ssl`、`ca-bundle`、`ca-certificates`
- DNS：`smartdns`、`mosdns`、`adguardhome`
- 代理：`luci-app-openclash`、`luci-app-passwall`
- DDNS：`ddns-go`、`luci-app-ddns-go`
- 远程连接：`zerotier`、`easytier`
- 运维：`ttyd`、`luci-app-autoreboot`、`netdata`、`luci-app-statistics`
- 存储：`luci-app-diskman`、`samba4-server`、USB 存储和常见文件系统支持
- Docker：`docker`、`dockerd`、`containerd`、`docker-compose`、`luci-app-dockerman`
- 内存压缩：`zram-swap`

完整包计划见 [targets/ax6600/package-plan.yml](targets/ax6600/package-plan.yml) 和 [docs/final-package-list.md](docs/final-package-list.md)。

## 推荐使用方式

为了稳定、少折腾，建议按下面方式使用：

1. 不要在路由器上执行全量 `apk upgrade`。
2. 需要升级时，从本仓库 Releases 下载新的 `sysupgrade.bin` 整包升级。
3. OpenClash 和 PassWall 可以都编译进固件，但运行时建议只启用一个主透明代理。
4. DNS 链路建议保持简单，不要让 AdGuardHome、mosdns、smartdns、OpenClash DNS 互相循环转发。
5. Docker 已内置，但建议接外置硬盘后再长期运行容器。
6. zram 保持默认压缩算法，不强行切换到内核不支持的 zstd。
7. LuCI 里的 `System -> Plugins` 是新版 LuCI 自带插件页，没有插件挂载时为空，属于正常现象。

## 自定义构建

你可以通过 GitHub Actions 手动构建：

1. 打开 `Actions`
2. 选择 `Build AX6600 Firmware`
3. 点击 `Run workflow`
4. 按需要填写：
   - `optional_profiles`：额外启用的 profile
   - `replace_default_optional_profiles`：是否替换默认 profile
   - `package_overrides`：临时增删包，例如 `pkgA -pkgB`
   - `publish_release`：是否发布到 Releases

默认 profile 定义在 [targets/ax6600/manifest.yml](targets/ax6600/manifest.yml)，包计划定义在 [targets/ax6600/package-plan.yml](targets/ax6600/package-plan.yml)。

## 仓库结构

```text
.github/workflows/          GitHub Actions 构建、发布、同步流程
benchmarks/                 性能和运行基线
config/ax6600/              分层 OpenWrt 配置片段
decisions/                  架构决策记录 ADR
docs/                       运维、包列表和维护文档
feeds/custom.conf           第三方包 feed
patches/firmware-layer/     产品层补丁
scripts/                    配置组装、校验、发布元数据脚本
targets/ax6600/             设备 manifest、上游、兼容矩阵、功能策略
```

## AI 维护控制面

这个项目专门为长期维护设计。AI 或维护者不需要每次重新理解整个仓库，只需要从这些入口读取状态：

- [targets/ax6600/manifest.yml](targets/ax6600/manifest.yml)
- [targets/ax6600/upstreams.yml](targets/ax6600/upstreams.yml)
- [targets/ax6600/compat-matrix.yml](targets/ax6600/compat-matrix.yml)
- [targets/ax6600/feature-policy.yml](targets/ax6600/feature-policy.yml)
- [targets/ax6600/package-plan.yml](targets/ax6600/package-plan.yml)
- [benchmarks/baseline.yml](benchmarks/baseline.yml)
- [decisions/](decisions/)

核心原则是：上游可以更新，包可以调整，但 `NSS`、目标设备、构建成功、发布透明度和可回滚性不能退化。

## 上游与致谢

本项目参考并跟踪了以下项目：

- [zhyzhaogit/ax6600-source](https://github.com/zhyzhaogit/ax6600-source)
- [ones20250/immortalwrt_ipq](https://github.com/ones20250/immortalwrt_ipq)
- [ones20250/Openwrt-AX6600](https://github.com/ones20250/Openwrt-AX6600)
- [ZqinKing/wrt_release](https://github.com/ZqinKing/wrt_release)
- [immortalwrt/immortalwrt](https://github.com/immortalwrt/immortalwrt)

感谢 OpenWrt、ImmortalWrt、LuCI 和各第三方插件维护者。

## 免责声明

本项目是个人维护的开源固件构建项目，不提供任何刷机成功保证。刷机、改分区、刷 U-Boot、跨版本升级都可能导致设备无法启动。请确保你理解风险，并自行承担后果。

---

# AX6600 / RE-CS-02 OpenWrt Firmware

Sustainable OpenWrt / ImmortalWrt firmware builds for the JDCloud `RE-CS-02` / `AX6600` router.

This repository is the product layer of the firmware line. It does not simply copy another build repository. Instead, it keeps device policy, package selection, upstream sources, release rules, validation checks, and GitHub Actions workflows in machine-readable files so the project can be maintained over time.

## Project Status

- Device: `JDCloud RE-CS-02 / AX6600`
- OpenWrt target: `qualcommax/ipq60xx`
- Default source: `zhyzhaogit/ax6600-source@ax6600-stable`
- Firmware artifacts: both `factory.bin` and `sysupgrade.bin`
- Default LAN: `10.0.0.1`
- Default theme: `luci-theme-argon`
- Package manager: APK-based snapshots; this project does not mix in opkg/iStore by default

Download the latest firmware from [Releases](https://github.com/zhyzhaogit/ax6600-firmware/releases).

## Highlights

- NSS hardware acceleration is required and validated.
- GitHub Actions builds firmware automatically.
- Main-branch builds publish prereleases when successful.
- HTTPS package management support is built in through `wget-ssl`, `ca-bundle`, and `ca-certificates`.
- Chinese LuCI translations are selected when available, but missing translations do not block releases.
- Docker, Samba4, Diskman, USB storage, USB network adapters, OpenClash, PassWall, SmartDNS, MosDNS, AdGuardHome, ddns-go, EasyTier, and ZeroTier are compiled in by default.

## Which Image Should I Use?

| File | Use case |
| --- | --- |
| `*-factory.bin` | First flash from stock firmware, U-Boot Web recovery, or non-OpenWrt firmware |
| `*-sysupgrade.bin` | Upgrade from an existing OpenWrt / ImmortalWrt installation |

Flashing is risky. Make sure you have a backup, a recovery path, and the correct device model before using these images.

## Recommended Runtime Policy

- Do not run a full `apk upgrade` on the router. Prefer flashing a newly built `sysupgrade.bin`.
- Keep only one transparent proxy stack active at runtime. OpenClash and PassWall can both be installed, but they should not both own DNS and TPROXY rules at the same time.
- Keep the DNS chain simple. Avoid circular forwarding between AdGuardHome, MosDNS, SmartDNS, and proxy DNS components.
- Docker is included, but long-running containers are best used with external storage.
- Keep zram on the kernel-supported default compression algorithm.

## Custom Builds

Use the `Build AX6600 Firmware` workflow in GitHub Actions. The workflow supports optional profiles and package overrides, for example:

```text
package_overrides: pkgA -pkgB
```

The main configuration entry points are:

- [targets/ax6600/manifest.yml](targets/ax6600/manifest.yml)
- [targets/ax6600/package-plan.yml](targets/ax6600/package-plan.yml)
- [targets/ax6600/feature-policy.yml](targets/ax6600/feature-policy.yml)
- [feeds/custom.conf](feeds/custom.conf)

## Maintenance Model

The repository is designed for AI-assisted maintenance. Upstream changes are observed, classified, validated, and only then released. Required features such as NSS support, target correctness, package-plan integrity, and release transparency should not regress.

## Disclaimer

This is a personal open-source firmware build project. No warranty is provided. Flashing custom firmware, changing bootloaders, or upgrading across incompatible layouts can brick your router. Use at your own risk.
