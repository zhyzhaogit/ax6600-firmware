#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?source directory is required}"
FEEDS_FILE="${2:?feeds file is required}"
PATCH_DIR="${3:?patch directory is required}"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "source directory not found: ${SOURCE_DIR}" >&2
  exit 1
fi

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
  while IFS= read -r -d '' patch_file; do
    git -C "${SOURCE_DIR}" apply --whitespace=nowarn "${patch_file}"
  done < <(find "${PATCH_DIR}" -type f -name '*.patch' -print0 | sort -z)
fi
