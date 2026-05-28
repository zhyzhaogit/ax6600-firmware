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
  # Feed package patches are applied later after feeds are installed
  while IFS= read -r -d '' patch_file; do
    git -C "${SOURCE_DIR}" apply --whitespace=nowarn "${patch_file}"
  done < <(find "${PATCH_DIR}" -maxdepth 1 -type f -name '*.patch' -print0 | sort -z)
fi

# Apply feed package patches after feeds are installed
# Patches should be organized as: patches/feed-packages/<feed-name>/<package-name>/*.patch
# Example: patches/feed-packages/packages/netdata/0001-fix-protobuf-compat.patch
if [[ -d "${PATCH_DIR}/feed-packages" ]]; then
  echo "Applying feed package patches..."
  while IFS= read -r -d '' patch_file; do
    # Extract feed name and package name from path
    rel_path="${patch_file#${PATCH_DIR}/feed-packages/}"
    feed_name="${rel_path%%/*}"
    remaining="${rel_path#*/}"
    package_name="${remaining%%/*}"

    # Determine the target directory based on feed
    case "${feed_name}" in
      packages)
        target_dir="${SOURCE_DIR}/feeds/packages"
        ;;
      luci)
        target_dir="${SOURCE_DIR}/feeds/luci"
        ;;
      routing)
        target_dir="${SOURCE_DIR}/feeds/routing"
        ;;
      telephony)
        target_dir="${SOURCE_DIR}/feeds/telephony"
        ;;
      video)
        target_dir="${SOURCE_DIR}/feeds/video"
        ;;
      *)
        echo "Warning: Unknown feed '${feed_name}', skipping patch: ${patch_file}" >&2
        continue
        ;;
    esac

    # Find the actual package directory
    pkg_dir=$(find "${target_dir}" -type d -name "${package_name}" 2>/dev/null | head -1)
    if [[ -z "${pkg_dir}" ]]; then
      echo "Warning: Package directory not found for '${package_name}' in feed '${feed_name}', skipping: ${patch_file}" >&2
      continue
    fi

    echo "Applying patch to ${feed_name}/${package_name}: $(basename "${patch_file}")"
    git -C "${pkg_dir}" apply --whitespace=nowarn "${patch_file}" 2>/dev/null || \
      (cd "${pkg_dir}" && patch -p1 < "${patch_file}") || \
      echo "Warning: Failed to apply patch: ${patch_file}" >&2
  done < <(find "${PATCH_DIR}/feed-packages" -type f -name '*.patch' -print0 | sort -z)
fi

if [[ -n "${OVERLAY_DIR}" && -d "${OVERLAY_DIR}" ]]; then
  mkdir -p "${SOURCE_DIR}/files"
  cp -a "${OVERLAY_DIR}/." "${SOURCE_DIR}/files/"
fi
