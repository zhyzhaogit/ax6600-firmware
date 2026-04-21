# Architecture

## Goal

Keep AX6600 firmware fast, traceable, and maintainable under frequent upstream movement.

## Design

- Source-level risk lives in `ax6600-source`.
- Product policy, config layering, and release gating live here.
- AI reads the control-plane files first and only then acts on references, reports, and patches.

## Control Plane

The AI control plane is implemented through:

- `manifest.yml`
- `upstreams.yml`
- `compat-matrix.yml`
- `feature-policy.yml`
- `benchmarks/baseline.yml`
- ADRs in `decisions/`

These files define what to track, what must not regress, and how to interpret upstream changes without rediscovering the project intent every time.

## Update Flow

1. Detect upstream movement.
2. Generate a diff or sync report.
3. Validate config, required features, and baseline policy.
4. Merge reviewed updates.
5. Release only from a validated state.
