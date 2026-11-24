-- Run AFTER loading data. Foreign keys and the secondary indexes commonly used
-- for TPC-H. The same logical set is created on SQL Server (sqlserver_indexes.sql)
-- so that both optimizers see equivalent physical designs.
ALTER TABLE nation   ADD INDEX idx_n_regionkey (n_regionkey);
ALTER TABLE supplier ADD INDEX idx_s_nationkey (s_nationkey);
ALTER TABLE customer ADD INDEX idx_c_nationkey (c_nationkey);
ALTER TABLE partsupp ADD INDEX idx_ps_suppkey (ps_suppkey);
ALTER TABLE orders   ADD INDEX idx_o_custkey (o_custkey), ADD INDEX idx_o_orderdate (o_orderdate);
ALTER TABLE lineitem ADD INDEX idx_l_partkey_suppkey (l_partkey, l_suppkey),
                     ADD INDEX idx_l_suppkey (l_suppkey),
                     ADD INDEX idx_l_shipdate (l_shipdate);
ANALYZE TABLE region, nation, part, supplier, partsupp, customer, orders, lineitem;
