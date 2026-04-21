# Operations Runbook

## Purpose

This repository is designed so future AI runs can make good decisions without re-learning the project from scratch.

## First Files To Read

1. `targets/ax6600/manifest.yml`
2. `targets/ax6600/upstreams.yml`
3. `targets/ax6600/compat-matrix.yml`
4. `targets/ax6600/feature-policy.yml`
5. `benchmarks/baseline.yml`
6. `decisions/ADR-*.md`

## Standard Update Loop

1. Run `sync-watch` to detect upstream movement.
2. Review the updated `reference_state` and the generated sync report.
3. Run `config-diff` to classify configuration, workflow, and script changes from reference repositories.
4. Decide whether the change belongs in:
   - config fragments
   - firmware-layer scripts or workflows
   - `ax6600-source`
5. Run `canary-build` before merging.
6. Update benchmark metrics after real-device validation.
7. Release only from validated source and metrics.

## Rules For AI

- Do not absorb changes from reference repositories wholesale.
- Do not prefer a newer source version over required NSS or performance traits.
- Treat bootloader, partition, GPT, and U-Boot changes as blocked by default.
- Keep source-level and firmware-level changes separated.
- When in doubt, update ADRs or the compatibility matrix instead of hiding decisions in code.

## When To Touch `ax6600-source`

Use `ax6600-source` only when the change must live in the actual source tree:

- IPQ/NSS source changes
- target fixes
- source-level build repairs

Prefer the firmware repository for package selection, feed registration, and release automation.
