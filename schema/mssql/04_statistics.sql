-- Full-scan statistics on every table so neither engine benefits from sampling
-- luck. Column statistics on non-indexed predicate columns are auto-created by
-- SQL Server on first use; creating them up front keeps the first timed run
-- from paying that cost and mirrors the MySQL histograms in schema/mysql/04_statistics.sql.

CREATE STATISTICS st_l_returnflag ON dbo.lineitem (l_returnflag) WITH FULLSCAN;
CREATE STATISTICS st_l_linestatus ON dbo.lineitem (l_linestatus) WITH FULLSCAN;
CREATE STATISTICS st_l_discount   ON dbo.lineitem (l_discount)   WITH FULLSCAN;
CREATE STATISTICS st_l_quantity   ON dbo.lineitem (l_quantity)   WITH FULLSCAN;
CREATE STATISTICS st_l_shipmode   ON dbo.lineitem (l_shipmode)   WITH FULLSCAN;
CREATE STATISTICS st_l_shipinstruct ON dbo.lineitem (l_shipinstruct) WITH FULLSCAN;
CREATE STATISTICS st_l_commitdate ON dbo.lineitem (l_commitdate) WITH FULLSCAN;
CREATE STATISTICS st_l_receiptdate ON dbo.lineitem (l_receiptdate) WITH FULLSCAN;
CREATE STATISTICS st_o_orderstatus ON dbo.orders (o_orderstatus) WITH FULLSCAN;
CREATE STATISTICS st_o_orderpriority ON dbo.orders (o_orderpriority) WITH FULLSCAN;
CREATE STATISTICS st_o_comment    ON dbo.orders   (o_comment)    WITH FULLSCAN;
CREATE STATISTICS st_c_mktsegment ON dbo.customer (c_mktsegment) WITH FULLSCAN;
CREATE STATISTICS st_c_acctbal    ON dbo.customer (c_acctbal)    WITH FULLSCAN;
CREATE STATISTICS st_c_phone      ON dbo.customer (c_phone)      WITH FULLSCAN;
CREATE STATISTICS st_p_brand      ON dbo.part (p_brand)      WITH FULLSCAN;
CREATE STATISTICS st_p_type       ON dbo.part (p_type)       WITH FULLSCAN;
CREATE STATISTICS st_p_size       ON dbo.part (p_size)       WITH FULLSCAN;
CREATE STATISTICS st_p_container  ON dbo.part (p_container)  WITH FULLSCAN;
CREATE STATISTICS st_p_name       ON dbo.part (p_name)       WITH FULLSCAN;
CREATE STATISTICS st_s_comment    ON dbo.supplier (s_comment) WITH FULLSCAN;
CREATE STATISTICS st_n_name       ON dbo.nation (n_name)     WITH FULLSCAN;
CREATE STATISTICS st_r_name       ON dbo.region (r_name)     WITH FULLSCAN;
GO

UPDATE STATISTICS dbo.region   WITH FULLSCAN;
UPDATE STATISTICS dbo.nation   WITH FULLSCAN;
UPDATE STATISTICS dbo.supplier WITH FULLSCAN;
UPDATE STATISTICS dbo.customer WITH FULLSCAN;
UPDATE STATISTICS dbo.part     WITH FULLSCAN;
UPDATE STATISTICS dbo.partsupp WITH FULLSCAN;
UPDATE STATISTICS dbo.orders   WITH FULLSCAN;
UPDATE STATISTICS dbo.lineitem WITH FULLSCAN;
GO
