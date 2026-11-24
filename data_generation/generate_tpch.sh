#!/usr/bin/env bash
# Generate TPC-H data with dbgen.
#
# Usage:  ./data_generation/generate_tpch.sh <scale_factor> [output_dir]
# Example: ./data_generation/generate_tpch.sh 1          -> data_generation/data/sf1/*.tbl
#
# Data source: the TPC-H benchmark data generator (dbgen). The official kit is published by
# the Transaction Processing Performance Council (https://www.tpc.org/tpch/); this script uses the
# public GitHub mirror https://github.com/electrum/tpch-dbgen, which contains the same dbgen/qgen
# sources and builds on Linux/macOS without registration.
# The generated .tbl files are large and are NOT committed (see .gitignore); regenerate them here.
set -euo pipefail

SF="${1:?usage: $0 <scale_factor> [output_dir]}"
HERE="$(cd "$(dirname "$0")" && pwd)"
KIT="$HERE/tpch-dbgen"
OUT="${2:-$HERE/data/sf${SF}}"

if [ ! -d "$KIT" ]; then
  git clone --depth 1 https://github.com/electrum/tpch-dbgen "$KIT"
fi
if [ ! -x "$KIT/dbgen" ]; then
  # DATABASE=ORACLE only selects the dialect macros used by qgen; dbgen output is identical.
  make -C "$KIT" MACHINE=LINUX DATABASE=ORACLE
fi

mkdir -p "$OUT"
( cd "$KIT" && DSS_PATH="$OUT" ./dbgen -s "$SF" -f )
# Checksums let two independent generation runs be compared (requirement NFR-01).
( cd "$OUT" && sha256sum *.tbl > checksums.sha256 )
echo "Generated TPC-H data at scale factor $SF in $OUT"
ls -lh "$OUT"
