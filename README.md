# ax6600-firmware

This repository is the product layer for the AX6600 / RE-CS-02 firmware line.

It owns:

- machine-readable control-plane files for future AI maintenance
- config fragments and package tiering
- firmware-layer patches and source preparation hooks
- canary validation and release workflows
- release metadata and benchmark policy

It does not own upstream source history. That lives in `ax6600-source`.

## Layout

- `targets/ax6600/manifest.yml`: device, source, config, and validation entrypoint
- `targets/ax6600/upstreams.yml`: upstream registry and watched references
- `targets/ax6600/compat-matrix.yml`: known-good source combinations
- `targets/ax6600/feature-policy.yml`: non-regression policy
- `config/ax6600/`: layered config fragments
- `feeds/custom.conf`: custom package feeds for optional profiles
- `scripts/`: control-plane and validation helpers
- `.github/workflows/`: sync, diff, canary, and release automation
- `docs/operations.md`: the day-2 maintenance loop for AI and humans

## Bootstrap

1. Create the dedicated `ax6600-source` repository on GitHub.
2. Update `targets/ax6600/upstreams.yml` so `source-primary` points at your real repo.
3. Push this repository to GitHub and enable Actions.
4. Run `sync-watch` and `config-diff` once to create the initial reference state.
5. Run `canary-build` against the selected source branch before promoting any release.
6. Copy `benchmarks/runtime-metrics.example.yml` to `benchmarks/runtime-metrics.yml` and replace it with measured values before the first real release.
7. Run `python scripts/bootstrap_identity.py --github-user <your-user>` to point `source-primary` at your real source repository.

## Day-2 Loop

1. `sync-watch` detects upstream movement and refreshes `compat-matrix.yml` reference state.
2. `config-diff` classifies reference repository changes into absorbable or review-only buckets.
3. `canary-build` validates config assembly, required features, and source-tree preparation.
4. `release` is allowed only after required features and benchmark policy pass.

## Default Package Direction

The default assembled profile now includes:

- `services`
- `memory-boost`
- `proxy-stack`
- `connectivity`
- `storage-nas`
- `usb-network`
- `docker`

That means the baseline release path is aimed at an opinionated AX6600 image with:

- `zram-swap`
- `luci-app-athena-led`
- `luci-app-openclash`
- `luci-app-homeproxy`
- `luci-app-passwall`
- `smartdns`
- `mosdns`
- `adguardhome`
- `tailscale`
- `zerotier`
- `luci-app-diskman`
- `samba4-server`
- `ksmbd-server`
- `docker`
- `dockerd`
- `luci-app-dockerman`

The full package manifest is tracked in `targets/ax6600/package-plan.yml` and documented in `docs/final-package-list.md`.

You can still add or remove packages at build time through workflow inputs.
