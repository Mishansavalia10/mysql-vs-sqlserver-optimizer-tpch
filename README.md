# MySQL vs SQL Server: how much does optimizer maturity matter?

Group project for COMP.8157 (Advanced Database Topics), University of Windsor, Fall 2026. Team 4.

We are comparing how MySQL and Microsoft SQL Server plan and run the same queries. Both are cost-based, client-server databases, but SQL Server's optimizer has decades of development behind it, while MySQL only gained hash joins in version 8.0.18 (2019). The question: has MySQL caught up, or are there query shapes where the two engines still make noticeably different choices?

We use the standard TPC-H benchmark (22 queries) on identical data in both engines, run locally on one machine so that network latency does not affect the comparison. For each query we look at the join order, the join algorithm, and how far the optimizer's row-count estimates were from the actual counts.

## Repository layout

```
docs/
  proposals/            pre-proposal (D.1) and full proposal (D.2.1)
  reports/              midterm status report (D.3.1) and team contribution form (D.3.1.1)
  requirements/         user requirements and analysis document (D.4.1)
  individual_reports/   individual contribution reports (D.3.2)
config/                 config.example.ini, a connection-settings template
data_generation/        TPC-H data generation
schema/                 table definitions for MySQL and SQL Server
harness/                query runner and plan capture
parser/                 plan parsing
analysis/               estimation-error analysis
results/                raw plans, charts and tables
```

## Setup

Copy `config/config.example.ini` to `config/config.ini` and enter your own connection details. `config.ini` is gitignored, so credentials stay local. Generated TPC-H data files are also gitignored because of their size.

Tools: Python 3, MySQL Community Edition 8.0.18+, SQL Server Developer Edition, and the TPC-H toolkit (dbgen/qgen) from [tpc.org](https://www.tpc.org/tpch/).

## Project change

The first pre-proposal (`docs/proposals/D1_Project_Pre-Proposal.docx`) compared SQLite with SQL Server. We changed this to MySQL vs SQL Server because an embedded engine and a client-server engine differ in far more than their optimizers, which would confound the results. The full proposal (D.2.1) reflects the final plan.

## Task tracking

[Hive board](https://app.hive.com/workspace/No5EjiEYZTsGaS9yt?actionViewId=E4zjd25RAaGnxmTRq&projectId=FnzQvgdoo6HEjKDJK)

## Team

| Name | GitHub | Focus |
|---|---|---|
| Mishan Savalia | [@Mishansavalia10](https://github.com/Mishansavalia10) | Documentation, proposals, project tracking |
| Arya Chauhan | [@arya-003](https://github.com/arya-003) | Implementation: data loading, query harness, plan capture |
| Mukesh Manikandan | [@mukeshmanikandan](https://github.com/mukeshmanikandan) | Validation, analysis and results |

Instructor: Dr. Andreas S. Maniatis.
