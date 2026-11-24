"""Check that MySQL and SQL Server hold identical row counts for every TPC-H table.

    python -m data_generation.verify_counts            # compares both engines
    python -m data_generation.verify_counts --mysql-only

Exit status is 1 on any mismatch, so it can be used as a gate before an experiment run.
"""
from __future__ import annotations

import argparse
import sys

from harness.common import TPCH_TABLES, mysql_connect, sqlserver_connect


def counts(conn) -> dict[str, int]:
    cur = conn.cursor()
    out = {}
    for t in TPCH_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        out[t] = cur.fetchone()[0]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mysql-only", action="store_true")
    args = ap.parse_args()
    my = counts(mysql_connect())
    if args.mysql_only:
        for t, n in my.items():
            print(f"{t:<9} {n:>10,}")
        return
    ms = counts(sqlserver_connect())
    bad = 0
    print(f"{'table':<10}{'mysql':>12}{'sqlserver':>12}  status")
    for t in TPCH_TABLES:
        ok = my[t] == ms[t]
        bad += not ok
        print(f"{t:<10}{my[t]:>12,}{ms[t]:>12,}  {'OK' if ok else 'MISMATCH'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
