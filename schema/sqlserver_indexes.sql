-- Run AFTER loading data. Mirrors schema/mysql_indexes.sql.
CREATE INDEX idx_n_regionkey ON nation (n_regionkey);
CREATE INDEX idx_s_nationkey ON supplier (s_nationkey);
CREATE INDEX idx_c_nationkey ON customer (c_nationkey);
CREATE INDEX idx_ps_suppkey ON partsupp (ps_suppkey);
CREATE INDEX idx_o_custkey ON orders (o_custkey);
CREATE INDEX idx_o_orderdate ON orders (o_orderdate);
CREATE INDEX idx_l_partkey_suppkey ON lineitem (l_partkey, l_suppkey);
CREATE INDEX idx_l_suppkey ON lineitem (l_suppkey);
CREATE INDEX idx_l_shipdate ON lineitem (l_shipdate);
GO
EXEC sp_updatestats;
GO
