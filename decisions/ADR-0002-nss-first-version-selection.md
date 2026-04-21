# ADR-0002: Favor NSS-Capable IPQ Upstream Over The Most Generic Upstream

## Status

Accepted

## Context

This firmware line exists to be meaningfully better than a generic self-build. For AX6600, that means NSS and IPQ60xx-specific behavior are first-class requirements, not optional bonuses.

## Decision

Start from `ones20250/immortalwrt_ipq` as the bootstrap source and treat more generic upstreams as fallback references until measured evidence shows they can preserve required features.

## Consequences

- Version recency alone is not enough to justify source switching.
- New upstreams must prove that required features remain intact before promotion.
- The compatibility matrix records which combinations are safe to release.
