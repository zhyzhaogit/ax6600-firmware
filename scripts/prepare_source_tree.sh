#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?source directory is required}"
FEEDS_FILE="${2:?feeds file is required}"
PATCH_DIR="${3:?patch directory is required}"
OVERLAY_DIR="${4:-}"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "source directory not found: ${SOURCE_DIR}" >&2
  exit 1
fi

# Convert to absolute paths to avoid path resolution issues
SOURCE_DIR="$(cd "${SOURCE_DIR}" && pwd)"
PATCH_DIR="$(cd "${PATCH_DIR}" && pwd)"

if [[ -f "${FEEDS_FILE}" ]]; then
  touch "${SOURCE_DIR}/feeds.conf.default"
  while IFS= read -r line; do
    [[ -z "${line}" || "${line}" == \#* ]] && continue
    if ! grep -Fqx "${line}" "${SOURCE_DIR}/feeds.conf.default"; then
      echo "${line}" >> "${SOURCE_DIR}/feeds.conf.default"
    fi
  done < "${FEEDS_FILE}"
fi

if [[ -d "${PATCH_DIR}" ]]; then
  # Only apply patches from the root of PATCH_DIR, not from feed-packages subdirectory
  # Feed package patches are applied later in the workflow after feeds are installed
  while IFS= read -r -d '' patch_file; do
    git -C "${SOURCE_DIR}" apply --whitespace=nowarn "${patch_file}"
  done < <(find "${PATCH_DIR}" -maxdepth 1 -type f -name '*.patch' -print0 | sort -z)
fi

if [[ -n "${OVERLAY_DIR}" && -d "${OVERLAY_DIR}" ]]; then
  mkdir -p "${SOURCE_DIR}/files"
  cp -a "${OVERLAY_DIR}/." "${SOURCE_DIR}/files/"
fi
