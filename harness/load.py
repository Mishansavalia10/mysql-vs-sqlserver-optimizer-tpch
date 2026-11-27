"""Create the TPC-H schema on one engine and bulk-load dbgen output.

Runs schema/<engine>/NN_*.sql in order, then checks every table's row count
against the manifest.json written by data_generation.generate.

    python -m harness.load --engine mysql --data data/sf1
    python -m harness.load --engine mssql --data data/sf1 --server-data-dir /data/sf1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from harness.db import ConnSettings, connect

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema"


def split_mysql(script: str) -> list[str]:
    """Split on ';' at end of line; drop chunks that are only comments."""
    out = []
    for chunk in re.split(r";[ \t]*(?:\r?\n|$)", script):
        body = "\n".join(l for l in chunk.splitlines() if not l.strip().startswith("--")).strip()
        if body:
            out.append(chunk.strip())
    return out


def split_mssql(script: str) -> list[str]:
    """Split on GO batch separators (a line containing only GO)."""
    out = []
    for chunk in re.split(r"^\s*GO\s*$", script, flags=re.IGNORECASE | re.MULTILINE):
        body = "\n".join(l for l in chunk.splitlines() if not l.strip().startswith("--")).strip()
        if body:
            out.append(chunk.strip())
    return out


def ensure_database(engine: str) -> None:
    name = ConnSettings.from_env(engine).database
    if not re.fullmatch(r"\w+", name):
        sys.exit(f"refusing unsafe database name {name!r}")
    db = connect(engine, database=False)
    if engine == "mysql":
        db.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    else:
        db.execute(f"IF DB_ID('{name}') IS NULL CREATE DATABASE {name}")
    db.close()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["mysql", "mssql"], required=True)
    ap.add_argument("--data", type=Path, required=True, help="directory with <table>.tbl and manifest.json")
    ap.add_argument("--server-data-dir",
                    help="SQL Server only: the data dir as the server sees it (default /data/<name of --data>)")
    args = ap.parse_args(argv)

    data = args.data.resolve()
    manifest = json.loads((data / "manifest.json").read_text())
    data_dir = str(data) if args.engine == "mysql" else (args.server_data_dir or f"/data/{data.name}")
    split = split_mysql if args.engine == "mysql" else split_mssql

    ensure_database(args.engine)
    db = connect(args.engine)
    print(f"{args.engine} {db.version()}  <- {data}")

    for f in sorted((SCHEMA / args.engine).glob("[0-9][0-9]_*.sql")):
        t0 = time.perf_counter()
        for stmt in split(f.read_text().replace("{data_dir}", data_dir)):
            db.execute(stmt)
        print(f"  {f.name:<22} {time.perf_counter() - t0:8.1f}s")

    bad = 0
    for table, info in manifest["tables"].items():
        n = _count(db, table)
        flag = "" if n == info["rows"] else "  MISMATCH"
        bad += bool(flag)
        print(f"  {table:<9} {n:>12,} rows{flag}")
    db.close()
    if bad:
        sys.exit(f"{bad} table(s) did not load the expected row count")


def _count(db, table: str) -> int:
    cur = db.conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    n = cur.fetchone()[0]
    cur.fetchall()
    cur.close()
    return int(n)


if __name__ == "__main__":
    main()
