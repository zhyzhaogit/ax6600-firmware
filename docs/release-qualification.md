# AX6600 Release Qualification

The build pipeline accepts a configured source key and an optional exact source ref. Use the
configured branch for routine builds and an immutable commit SHA for candidate qualification or
reproduction:

```text
source_key=source-primary
source_ref=33de2be0eb62b6959c48d26b4b70376bf4d14d8c
```

`Canary Build` and `Build AX6600 Firmware` resolve the ref with the same source resolver and run the
same feed, patch, config-copy, `make defconfig`, required-feature, and package-plan preparation path.
Enable `run_full_build` in the canary only when a complete, non-publishing firmware compile is needed.

## Source candidate workflow

The source repository's `Source Rebase` workflow maintains one reusable candidate branch for each
upstream repository/branch pair. A green run means the candidate was rebased, published, and has an
open reviewable pull request. It never updates `ax6600-stable` and it never deletes legacy branches.
A failed push or pull-request operation leaves the run non-green and records the reason in the JSON
and Markdown artifacts.

Promotion remains a human decision. Before changing `ax6600-stable`, run the firmware preparation
gates, a full build, artifact inspection, and device qualification against the exact candidate SHA.

## Build-valid and runtime-valid

A successful build proves config assembly, feed patching, compilation, expected artifact presence,
and recorded provenance. It does not prove that the router boots, radios work, NSS offload behaves as
expected, upgrades preserve settings, or recovery is available.

Releases are classified as follows:

- Prerelease: may be published when the source is recorded as build-successful but runtime validation
  is still pending, if `benchmarks/baseline.yml` permits it.
- Stable release: requires a successful known-good source entry plus runtime evidence whose config
  SHA256 and firmware artifact SHA256 match the build provenance exactly.

When device testing is complete, set `runtime_validation_status` in
`targets/ax6600/compat-matrix.yml` to a passing value and add evidence in this form:

```yaml
runtime_validation_status: passed
runtime_validation_evidence:
  config_sha256: "<sha256 of final.config>"
  artifact_sha256s:
    - "<sha256 of the firmware image tested on the router>"
  report: "<path or URL to the qualification record>"
```

Do not copy synthetic values from `benchmarks/runtime-metrics.example.yml`; that file is only a
parser fixture.

## Release workflow compatibility

`Publish Build Release` loads the commit that produced the selected build into an isolated worktree
for build-era package-plan validation. The main worktree stays on the commit that started the release
run, so the current release policy remains authoritative. The workflow supports build artifacts
produced after provenance and release eligibility were introduced. Older artifacts without
`build-provenance.json` are intentionally not publishable through this workflow; rebuild them from an
exact recorded source ref instead.
