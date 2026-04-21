#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?source dir required}"
DEST_DIR="${2:?destination dir required}"

mkdir -p "${DEST_DIR}"

TARGET_DIR="$(find "${SOURCE_DIR}/bin/targets" -mindepth 2 -maxdepth 2 -type d | head -n 1 || true)"
if [[ -z "${TARGET_DIR}" ]]; then
  echo "No target output directory found under ${SOURCE_DIR}/bin/targets" >&2
  exit 1
fi

mkdir -p "${DEST_DIR}/factory" "${DEST_DIR}/sysupgrade" "${DEST_DIR}/meta"

find "${TARGET_DIR}" -maxdepth 1 -type f \( -name '*factory*' -o -name '*factory*.bin' -o -name '*factory*.img*' \) -exec cp -f {} "${DEST_DIR}/factory/" \;
find "${TARGET_DIR}" -maxdepth 1 -type f \( -name '*sysupgrade*' -o -name '*sysupgrade*.bin' -o -name '*sysupgrade*.img*' \) -exec cp -f {} "${DEST_DIR}/sysupgrade/" \;

for meta in sha256sums profiles.json *.buildinfo *.manifest config.seed; do
  find "${TARGET_DIR}" -maxdepth 1 -type f -name "${meta}" -exec cp -f {} "${DEST_DIR}/meta/" \;
done

SUMMARY_FILE="${DEST_DIR}/meta/artifact-summary.md"
{
  echo "# Firmware Artifact Summary"
  echo
  echo "- target_dir: \`${TARGET_DIR}\`"
  echo "- factory_count: $(find "${DEST_DIR}/factory" -maxdepth 1 -type f | wc -l)"
  echo "- sysupgrade_count: $(find "${DEST_DIR}/sysupgrade" -maxdepth 1 -type f | wc -l)"
} > "${SUMMARY_FILE}"

if [[ "$(find "${DEST_DIR}/factory" -maxdepth 1 -type f | wc -l)" -eq 0 ]]; then
  echo "No factory artifacts collected" >&2
  exit 1
fi

if [[ "$(find "${DEST_DIR}/sysupgrade" -maxdepth 1 -type f | wc -l)" -eq 0 ]]; then
  echo "No sysupgrade artifacts collected" >&2
  exit 1
fi
