#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="${1:?repository in owner/name form is required}"
SOURCE_REF="${2:?source ref is required}"
DESTINATION="${3:?destination directory is required}"

if [[ ! "${REPOSITORY}" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "invalid repository: ${REPOSITORY}" >&2
  exit 2
fi
if [[ ! "${SOURCE_REF}" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$ ]] || [[ "${SOURCE_REF}" == *..* ]]; then
  echo "invalid source ref: ${SOURCE_REF}" >&2
  exit 2
fi
if [[ -e "${DESTINATION}" ]]; then
  echo "destination already exists: ${DESTINATION}" >&2
  exit 2
fi

mkdir -p "${DESTINATION}"
git -C "${DESTINATION}" init --quiet
git -C "${DESTINATION}" remote add origin "https://github.com/${REPOSITORY}.git"
git -C "${DESTINATION}" -c protocol.version=2 fetch --depth 1 origin "${SOURCE_REF}"
git -C "${DESTINATION}" checkout --detach --quiet FETCH_HEAD
git -C "${DESTINATION}" rev-parse HEAD
