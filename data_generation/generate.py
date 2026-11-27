"""Generate TPC-H data with dbgen and normalize it for bulk loading.

dbgen writes '|'-delimited .tbl files with a trailing '|' on every line. MySQL's
LOAD DATA and SQL Server's BULK INSERT both handle a plain '|' delimiter, but the
trailing separator would create a phantom empty column, so it is stripped here.

Usage:
    python -m data_generation.generate --sf 1 --out data/sf1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DBGEN = HERE / "tpch-kit" / "dbgen"

TABLES = ["region", "nation", "supplier", "customer", "part", "partsupp", "orders", "lineitem"]

# Row counts from the TPC-H spec (clause 4.2.5) at SF=1; nation/region are fixed.
SF1_ROWS = {
    "region": 5, "nation": 25, "supplier": 10_000, "customer": 150_000,
    "part": 200_000, "partsupp": 800_000, "orders": 1_500_000,
}


def expected_rows(table: str, sf: float) -> int | None:
    """Exact expected row count, or None for lineitem (varies around 6M*SF)."""
    if table in ("region", "nation"):
        return SF1_ROWS[table]
    if table == "lineitem":
        return None
    return int(SF1_ROWS[table] * sf)


def run_dbgen(dbgen_dir: Path, sf: float, out: Path) -> None:
    exe = dbgen_dir / "dbgen"
    if not exe.exists():
        sys.exit(f"dbgen not found at {exe}; run data_generation/build_dbgen.sh first")
    # dbgen writes into its cwd and needs dists.dss there.
    env = dict(os.environ, DSS_CONFIG=str(dbgen_dir), DSS_PATH=str(out))
    subprocess.run([str(exe), "-s", str(sf), "-f", "-q"], cwd=dbgen_dir, env=env, check=True)


def strip_trailing_delimiter(src: Path, dst: Path) -> int:
    """Copy src to dst without the trailing '|' on each line; return line count."""
    n = 0
    with src.open("rb") as fin, dst.open("wb") as fout:
        for line in fin:
            line = line.rstrip(b"\r\n")
            if line.endswith(b"|"):
                line = line[:-1]
            fout.write(line + b"\n")
            n += 1
    return n


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sf", type=float, default=1.0, help="TPC-H scale factor (default 1)")
    ap.add_argument("--out", type=Path, required=True, help="output directory for <table>.tbl files")
    ap.add_argument("--dbgen-dir", type=Path, default=DEFAULT_DBGEN)
    args = ap.parse_args(argv)

    out = args.out.resolve()
    raw = out / "_raw"
    raw.mkdir(parents=True, exist_ok=True)

    print(f"Generating TPC-H SF={args.sf} into {out}")
    run_dbgen(args.dbgen_dir.resolve(), args.sf, raw)

    manifest = {"scale_factor": args.sf, "tables": {}}
    for t in TABLES:
        n = strip_trailing_delimiter(raw / f"{t}.tbl", out / f"{t}.tbl")
        exp = expected_rows(t, args.sf)
        if exp is not None and n != exp:
            sys.exit(f"{t}: generated {n} rows, expected {exp}")
        manifest["tables"][t] = {"rows": n, "sha256": sha256(out / f"{t}.tbl")}
        print(f"  {t:<9} {n:>12,} rows")
    shutil.rmtree(raw)

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {out / 'manifest.json'}")


if __name__ == "__main__":
    main()
