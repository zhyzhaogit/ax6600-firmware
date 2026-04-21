# ADR-0001: Keep Source And Firmware As Separate Repositories

## Status

Accepted

## Context

AX6600 optimization needs two different kinds of change:

- source-level IPQ/NSS work that must stay close to upstream
- product-level config, packaging, release, and policy decisions

Mixing them in one long-lived repository makes it harder for future AI runs to understand which changes are safe to absorb and which changes are hardware-sensitive.

## Decision

Use two repositories:

- `ax6600-source` for source-level changes
- `ax6600-firmware` for product policy and release automation

Keep the AI control plane inside `ax6600-firmware` through machine-readable YAML files.

## Consequences

- Upstream rebases become simpler to reason about.
- Release and policy logic can evolve without polluting source history.
- Future AI runs get a stable entrypoint for intent and non-regression rules.
