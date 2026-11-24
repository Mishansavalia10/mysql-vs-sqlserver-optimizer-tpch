"""Load TPC-H .tbl files into SQL Server.

    python -m data_generation.load_sqlserver --data data_generation/data/sf1
    python -m data_generation.load_sqlserver --data ... --method pyodbc

Two methods:
- bulk (default): BULK INSERT. The path is read by the SQL Server service, so this works
  when SQL Server runs on the same machine as the files (the setup this project uses).
- pyodbc: client-side batched INSERT with fast_executemany. Slower, but works when the
  server cannot see the files.

Indexes are created after loading, mirroring data_generation/load_mysql.py.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from harness.common import REPO_ROOT, TPCH_COLUMNS, TPCH_TABLES, run_sql_file, sqlserver_connect


def _rows(path: Path, ncols: int):
    with path.open(encoding="latin-1") as f:
        for line in f:
            parts = line.rstrip("\n").split("|")
            yield tuple(parts[:ncols])  # last element after the trailing '|' is empty


def load(data_dir: Path, method: str = "bulk", skip_indexes: bool = False) -> dict[str, int]:
    conn = sqlserver_connect()
    cur = conn.cursor()
    run_sql_file(cur, REPO_ROOT / "schema" / "sqlserver_schema.sql", split_on_go=True)
    for table in TPCH_TABLES:
        path = (data_dir / f"{table}.tbl").resolve()
        t0 = time.time()
        if method == "bulk":
            cur.execute(
                f"BULK INSERT {table} FROM '{path}' "
                "WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '|\\n', TABLOCK)"
            )
        else:
            cols = TPCH_COLUMNS[table]
            sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
            cur.fast_executemany = True
            batch = []
            for row in _rows(path, len(cols)):
                batch.append(row)
                if len(batch) == 50_000:
                    cur.executemany(sql, batch)
                    batch = []
            if batch:
                cur.executemany(sql, batch)
        print(f"loaded {table:<9} in {time.time() - t0:6.1f}s")
    if not skip_indexes:
        t0 = time.time()
        run_sql_file(cur, REPO_ROOT / "schema" / "sqlserver_indexes.sql", split_on_go=True)
        print(f"indexes + statistics in {time.time() - t0:.1f}s")
    counts = {}
    for table in TPCH_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]
    conn.close()
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--method", choices=["bulk", "pyodbc"], default="bulk")
    ap.add_argument("--skip-indexes", action="store_true")
    args = ap.parse_args()
    for table, n in load(args.data, args.method, args.skip_indexes).items():
        print(f"{table:<9} {n:>10,}")


if __name__ == "__main__":
    main()
