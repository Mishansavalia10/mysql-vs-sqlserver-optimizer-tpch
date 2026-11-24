"""Load TPC-H .tbl files into MySQL.

    python -m data_generation.load_mysql --data data_generation/data/sf1

Steps: (1) create tables, (2) bulk-load each file with LOAD DATA LOCAL INFILE,
(3) create secondary indexes and run ANALYZE TABLE, (4) print row counts.

Design notes
- dbgen rows end with a trailing '|', so the line terminator is '|\\n'.
- Indexes are created after loading. Loading row by row with indexes in place was
  far slower at SF >= 5, which is why bulk load and deferred indexing are used.
- The server must allow local_infile (SET GLOBAL local_infile = 1).
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from harness.common import REPO_ROOT, TPCH_COLUMNS, TPCH_TABLES, mysql_connect, run_sql_file


def load(data_dir: Path, skip_indexes: bool = False) -> dict[str, int]:
    conn = mysql_connect()
    cur = conn.cursor()
    run_sql_file(cur, REPO_ROOT / "schema" / "mysql_schema.sql")
    # Larger buffer pool helps bulk loads, but it can only be set at server start in
    # some deployments, so we only relax checks that are session-scoped.
    cur.execute("SET unique_checks = 0")
    cur.execute("SET foreign_key_checks = 0")
    for table in TPCH_TABLES:
        path = (data_dir / f"{table}.tbl").resolve()
        cols = ", ".join(TPCH_COLUMNS[table])
        t0 = time.time()
        cur.execute(
            f"LOAD DATA LOCAL INFILE '{path}' INTO TABLE {table} "
            f"FIELDS TERMINATED BY '|' LINES TERMINATED BY '|\\n' ({cols})"
        )
        print(f"loaded {table:<9} in {time.time() - t0:6.1f}s")
    cur.execute("SET unique_checks = 1")
    cur.execute("SET foreign_key_checks = 1")
    if not skip_indexes:
        t0 = time.time()
        run_sql_file(cur, REPO_ROOT / "schema" / "mysql_indexes.sql")
        print(f"indexes + ANALYZE in {time.time() - t0:.1f}s")
    counts = {}
    for table in TPCH_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]
    conn.close()
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, type=Path, help="directory containing the .tbl files")
    ap.add_argument("--skip-indexes", action="store_true")
    args = ap.parse_args()
    for table, n in load(args.data, args.skip_indexes).items():
        print(f"{table:<9} {n:>10,}")


if __name__ == "__main__":
    main()
