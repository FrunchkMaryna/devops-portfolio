#!/usr/bin/env bash
set -e
SRC_DIR="$(dirname "$0")/git-hooks"
DEST_DIR=".git/hooks"
for f in pre-commit pre-push post-commit; do
  cp "${SRC_DIR}/${f}" "${DEST_DIR}/${f}"
  chmod +x "${DEST_DIR}/${f}"
  echo "Installed ${f}"
done
