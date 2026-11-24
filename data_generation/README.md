# data_generation

| File | Role |
|---|---|
| `generate_tpch.sh` | Builds the TPC-H `dbgen` tool and writes the `.tbl` files for a scale factor |
| `load_mysql.py` | Creates the schema, bulk loads with `LOAD DATA LOCAL INFILE`, then adds indexes |
| `load_sqlserver.py` | Same for SQL Server using `BULK INSERT` (or `--method pyodbc`) |
| `verify_counts.py` | Compares row counts between the two engines |

**Dataset source.** TPC-H data is generated, not downloaded: `dbgen` from the TPC-H benchmark kit
(https://www.tpc.org/tpch/). `generate_tpch.sh` fetches the public mirror
https://github.com/electrum/tpch-dbgen, which carries the same generator. Expected row counts at SF 1:
lineitem 6,001,215, orders 1,500,000, partsupp 800,000, part 200,000, customer 150,000, supplier 10,000,
nation 25, region 5 (scale linearly for other scale factors).

```
./data_generation/generate_tpch.sh 1
python -m data_generation.load_mysql      --data data_generation/data/sf1
python -m data_generation.load_sqlserver  --data data_generation/data/sf1
python -m data_generation.verify_counts
```
The generated `.tbl` files are gitignored because of their size.
