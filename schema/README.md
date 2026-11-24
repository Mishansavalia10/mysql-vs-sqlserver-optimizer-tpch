# schema

TPC-H table definitions for both engines.

| File | Purpose |
|---|---|
| `mysql_schema.sql` | Creates the 8 TPC-H tables on MySQL 8.0.18+ (InnoDB) |
| `mysql_indexes.sql` | Secondary indexes and `ANALYZE TABLE`, run after loading |
| `sqlserver_schema.sql` | Creates the 8 TPC-H tables on SQL Server 2019+ |
| `sqlserver_indexes.sql` | Same indexes plus `sp_updatestats`, run after loading |

Both engines get the same logical design and the same secondary indexes, so the optimizers compare like with like.
Column definitions follow the TPC-H specification.
