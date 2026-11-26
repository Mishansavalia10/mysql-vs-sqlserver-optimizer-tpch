# MySQL vs SQL Server: how much does optimizer maturity matter?

Group project for COMP.8157 (Advanced Database Topics), University of Windsor, Fall 2026. Team 4.

We compare how MySQL 8 and Microsoft SQL Server plan and execute the same queries. Both are cost-based, client-server databases, but SQL Server's optimizer has decades of development behind it, while MySQL only gained hash joins in 8.0.18 (2019). Using the 22 TPC-H queries on identical data in both engines, run locally on one machine so network latency stays out of the comparison, we look at join order, join algorithm and how far the optimizer's row-count estimates are from the actual counts.

## How the pieces fit

```
dbgen (TPC-H) --> .tbl files --> load_mysql.py / load_sqlserver.py --> two databases, same data
                                                                         |
queries/mysql, queries/sqlserver --> run_queries.py --> latency.csv + captured plans (results/raw_plans)
                                                                         |
                          parser/ (one common plan structure) --> analysis/ --> tables and charts
```

## Repository layout

| Folder | What is in it |
|---|---|
| `data_generation/` | TPC-H data generation, loaders for both engines, row-count check |
| `schema/` | Table and index definitions for MySQL and SQL Server |
| `harness/` | Query runner, plan capture, the 22 queries per engine |
| `parser/` | MySQL and SQL Server plan parsers and the common `PlanNode` structure |
| `analysis/` | q-error metrics, query-shape classification, tables and charts |
| `results/` | Captured plans, latency data, generated tables and charts |
| `tests/` | Unit tests and a live-MySQL integration test |
| `config/` | `config.example.ini` connection template |
| `docs/` | Proposals, reports, requirements, design, deployment and user guide documents |

## Quick start

Requirements: Python 3.10+, MySQL Community 8.0.18+, SQL Server Developer Edition with the ODBC Driver 18 for SQL Server, `git` and a C compiler (to build `dbgen`).

```
pip install -r requirements.txt
cp config/config.example.ini config/config.ini        # then edit your connection details
./data_generation/generate_tpch.sh 1                   # TPC-H data at scale factor 1
python -m data_generation.load_mysql     --data data_generation/data/sf1
python -m data_generation.load_sqlserver --data data_generation/data/sf1
python -m data_generation.verify_counts
python -m harness.run_queries --engine both --sf 1
python -m analysis.report --sf 1
python -m pytest -q
```
Full instructions are in `docs/deployment/` and `docs/user_guide/`.

## Data

TPC-H data is produced by `dbgen` from the TPC-H benchmark kit (https://www.tpc.org/tpch/); `generate_tpch.sh` uses the public mirror https://github.com/electrum/tpch-dbgen. The generated files are large and are gitignored, so regenerate them with the script.

## Verification status

| Component | Status |
|---|---|
| Data generation, MySQL loader, MySQL query runner and plan capture, MySQL plan parser, analysis and report | Run against a live MySQL 8.0 on TPC-H at SF 0.01; all 22 queries execute and parse; 20 unit and integration tests pass |
| SQL Server loader, query runner, plan capture and plan parser | Implemented; the parser is unit-tested on a sample plan. Still to be run against a live SQL Server Developer instance and checked against SSMS |
| SF 1, 5 and 10 experiment runs | Not yet run; see the Hive board |

## Project change

The first pre-proposal compared SQLite with SQL Server. We changed to MySQL vs SQL Server because an embedded and a client-server engine differ in far more than their optimizers, which would confound the results.

## Task tracking

[Hive board](https://app.hive.com/workspace/No5EjiEYZTsGaS9yt?actionViewId=E4zjd25RAaGnxmTRq&projectId=FnzQvgdoo6HEjKDJK)

## Team

| Name | GitHub | Focus |
|---|---|---|
| Mishan Savalia | [@Mishansavalia10](https://github.com/Mishansavalia10) | Documentation, proposals, project tracking |
| Arya Chauhan | [@arya-003](https://github.com/arya-003) | Implementation: data loading, query harness, plan capture |
| Mukesh Manikandan | [@mukeshmanikandan](https://github.com/mukeshmanikandan) | Validation, analysis and results |

Instructor: Dr. Andreas S. Maniatis.
