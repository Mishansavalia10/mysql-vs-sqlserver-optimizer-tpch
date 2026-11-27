#!/usr/bin/env bash
# Build the TPC-H dbgen/qgen tools from gregrahn/tpch-kit (a maintained,
# Linux/macOS-buildable copy of the TPC-H 2.x tools).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$HERE/tpch-kit"
REPO="https://github.com/gregrahn/tpch-kit.git"
# Pin the commit so data is reproducible across machines.
COMMIT="${TPCH_KIT_COMMIT:-852ad0a5ee31ebefeed884cea4188781dd9613a3}"

if [[ ! -d "$KIT/.git" ]]; then
  git clone --quiet "$REPO" "$KIT"
fi
git -C "$KIT" fetch --quiet origin
git -C "$KIT" checkout --quiet "$COMMIT"

case "$(uname -s)" in
  Darwin) MACHINE=MACOS ;;
  *)      MACHINE=LINUX ;;
esac

make -C "$KIT/dbgen" -s clean >/dev/null 2>&1 || true
make -C "$KIT/dbgen" -s MACHINE="$MACHINE" DATABASE=POSTGRESQL CC=gcc

echo "dbgen built at $KIT/dbgen/dbgen"
