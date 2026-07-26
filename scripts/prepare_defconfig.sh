#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?source directory is required}"
ASSEMBLED_CONFIG="${2:?assembled config is required}"
CONFLICT_REPORT="${3:?feed conflict report is required}"
PATCH_REPORT="${4:?feed patch report is required}"
PATCH_JSON_REPORT="${5:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="$(cd "${SOURCE_DIR}" && pwd)"
ASSEMBLED_CONFIG="$(cd "$(dirname "${ASSEMBLED_CONFIG}")" && pwd)/$(basename "${ASSEMBLED_CONFIG}")"
CONFLICT_REPORT="$(cd "$(dirname "${CONFLICT_REPORT}")" && pwd)/$(basename "${CONFLICT_REPORT}")"
PATCH_REPORT="$(cd "$(dirname "${PATCH_REPORT}")" && pwd)/$(basename "${PATCH_REPORT}")"
if [[ -n "${PATCH_JSON_REPORT}" ]]; then
  PATCH_JSON_REPORT="$(cd "$(dirname "${PATCH_JSON_REPORT}")" && pwd)/$(basename "${PATCH_JSON_REPORT}")"
fi
PATCH_REPORT_ARGS=(--report "${PATCH_REPORT}")
if [[ -n "${PATCH_JSON_REPORT}" ]]; then
  PATCH_REPORT_ARGS+=(--json-report "${PATCH_JSON_REPORT}")
fi

pushd "${SOURCE_DIR}" >/dev/null
./scripts/feeds update -a
python "${REPO_ROOT}/scripts/prune_conflicting_feed_packages.py" \
  --source-root "${SOURCE_DIR}" \
  --report "${CONFLICT_REPORT}"
./scripts/feeds install -a
./scripts/feeds install -f -p mosdns mosdns luci-app-mosdns v2dat
python "${REPO_ROOT}/scripts/normalize_feed_versions.py" --source-root "${SOURCE_DIR}"
python "${REPO_ROOT}/scripts/apply_feed_patches.py" \
  --source-root "${SOURCE_DIR}" \
  --patch-root "${REPO_ROOT}/patches/firmware-layer/feed-packages" \
  "${PATCH_REPORT_ARGS[@]}"
cp "${ASSEMBLED_CONFIG}" .config
make defconfig
popd >/dev/null
