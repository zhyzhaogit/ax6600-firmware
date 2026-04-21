# ADR-0003: Separate Plugin Profiles By Operational Risk

## Status

Accepted

## Context

AX6600 users often want DNS acceleration, proxy stacks, and custom services, but bundling everything by default makes baseline validation noisy and increases regression risk.

## Decision

Split packages into three tiers:

- core: always-on essentials
- recommended: low-risk enhancements
- optional: higher-coupling services such as proxy stacks

Optional features remain easy to enable through config fragments and feeds, but they do not define baseline release health.

## Consequences

- Canary validation can stay focused on the stable core image.
- Optional profile failures do not automatically block all upstream sync work.
- AI can classify incoming reference changes by tier instead of treating every plugin as equally critical.
