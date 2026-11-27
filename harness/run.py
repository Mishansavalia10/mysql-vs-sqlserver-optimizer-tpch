"""Run the TPC-H queries on one engine, recording latency and optimizer plans.

For each query:
  1. run its setup statements (Q15 creates its view)
  2. capture the estimated plan (not executed)
  3. execute it --warmups times, then --runs times, timing each
  4. capture the actual plan (executes once more, with runtime statistics)
  5. run its teardown statements

Outputs (all under --results, default results/):
  latency/<run_id>.csv                one row per execution
  plans/<engine>/<run_id>/qNN.estimated.<json|xml>
  plans/<engine>/<run_id>/qNN.actual.<json|xml|tree>
  runs/<run_id>.json                  settings and server version for the run

    python -m harness.run --engine mysql --sf 1 --runs 5 --warmups 1
    python -m harness.run --engine mssql --sf 1 --runs 5 --mssql-maxdop 1
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from harness.db import connect
from harness.queries import queries, render

ROOT = Path(__file__).resolve().parent.parent

LATENCY_FIELDS = [
    "run_id", "engine", "server_version", "scale_factor", "query", "phase",
    "iteration", "elapsed_ms", "rows", "status", "error", "started_at_utc",
]


def parse_query_list(spec: str) -> list[int]:
    """'1,3,5-7' -> [1, 3, 5, 6, 7]"""
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    bad = [q for q in out if not 1 <= q <= 22]
    if bad:
        raise ValueError(f"TPC-H query numbers are 1-22, got {bad}")
    return out


def mssql_hints(maxdop: int | None, recompile: bool) -> str:
    opts = []
    if maxdop is not None:
        opts.append(f"MAXDOP {maxdop}")
    if recompile:
        opts.append("RECOMPILE")
    return f"\nOPTION ({', '.join(opts)})" if opts else ""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["mysql", "mssql"], required=True)
    ap.add_argument("--sf", type=float, required=True, help="scale factor the database was loaded with")
    ap.add_argument("--runs", type=int, default=5, help="timed executions per query (default 5)")
    ap.add_argument("--warmups", type=int, default=1, help="untimed-for-analysis warm-up runs (default 1)")
    ap.add_argument("--queries", default="1-22", help="e.g. 1,3,5-7 (default 1-22)")
    ap.add_argument("--results", type=Path, default=ROOT / "results")
    ap.add_argument("--no-plans", action="store_true", help="skip plan capture")
    ap.add_argument("--mssql-maxdop", type=int, default=None,
                    help="add OPTION (MAXDOP n); 1 forces serial plans like MySQL")
    ap.add_argument("--no-mssql-recompile", action="store_true",
                    help="reuse cached plans. By default SQL Server recompiles every run so "
                         "optimization time is included, as it is on MySQL")
    ap.add_argument("--tag", default="", help="free-text label stored in the run metadata")
    args = ap.parse_args(argv)

    qids = parse_query_list(args.queries)
    hints = mssql_hints(args.mssql_maxdop, not args.no_mssql_recompile) if args.engine == "mssql" else ""

    db = connect(args.engine)
    version = db.version()
    run_id = f"{args.engine}_sf{args.sf:g}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    plan_dir = args.results / "plans" / args.engine / run_id
    lat_path = args.results / "latency" / f"{run_id}.csv"
    meta_path = args.results / "runs" / f"{run_id}.json"
    for p in (plan_dir, lat_path.parent, meta_path.parent):
        p.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id, "engine": args.engine, "server_version": version,
        "scale_factor": args.sf, "runs": args.runs, "warmups": args.warmups,
        "queries": qids, "mssql_maxdop": args.mssql_maxdop,
        "mssql_recompile": args.engine == "mssql" and not args.no_mssql_recompile,
        "plans_captured": not args.no_plans, "tag": args.tag,
        "client_host": platform.node(), "client_python": platform.python_version(),
        "started_at_utc": now_utc(),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"{run_id}: {args.engine} {version}")

    all_q = {q.qid: q for q in queries(args.sf)}
    with lat_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LATENCY_FIELDS)
        w.writeheader()

        def record(qname, phase, i, ms, rows, status="ok", error=""):
            w.writerow({
                "run_id": run_id, "engine": args.engine, "server_version": version,
                "scale_factor": args.sf, "query": qname, "phase": phase, "iteration": i,
                "elapsed_ms": "" if ms is None else f"{ms:.3f}", "rows": "" if rows is None else rows,
                "status": status, "error": error, "started_at_utc": now_utc(),
            })
            fh.flush()

        for qid in qids:
            rq = render(all_q[qid], args.engine)
            sql = rq.sql + hints
            timed: list[float] = []
            try:
                for s in rq.setup:
                    db.execute(s)
                if not args.no_plans:
                    # same hints as the timed runs, so a MAXDOP 1 run gets serial plans
                    fmt, text = db.estimated_plan(sql)
                    (plan_dir / f"{rq.name}.estimated.{fmt}").write_text(text)
                for phase, n in (("warmup", args.warmups), ("timed", args.runs)):
                    for i in range(1, n + 1):
                        t0 = time.perf_counter()
                        rows = db.run(sql)
                        ms = (time.perf_counter() - t0) * 1000
                        record(rq.name, phase, i, ms, rows)
                        if phase == "timed":
                            timed.append(ms)
                if not args.no_plans:
                    fmt, text = db.actual_plan(sql)
                    (plan_dir / f"{rq.name}.actual.{fmt}").write_text(text)
            except Exception as e:  # keep going: one failing query should not sink the run
                record(rq.name, "error", 0, None, None, "error", f"{type(e).__name__}: {e}"[:500])
                traceback.print_exc()
            finally:
                for s in rq.teardown:
                    try:
                        db.execute(s)
                    except Exception:
                        pass
            med = sorted(timed)[len(timed) // 2] if timed else float("nan")
            print(f"  {rq.name}  median {med:10.1f} ms over {len(timed)} runs")

    meta["finished_at_utc"] = now_utc()
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    db.close()
    print(f"latency -> {lat_path}\nplans   -> {plan_dir}")


if __name__ == "__main__":
    main()
