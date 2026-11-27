-- Refresh index statistics and build histograms on the non-indexed columns the
-- TPC-H predicates filter on. MySQL's optimizer only uses column histograms it
-- has been told to build; SQL Server auto-creates column statistics, so this
-- step is what keeps the cardinality-estimation comparison fair.

ANALYZE TABLE region, nation, supplier, customer, part, partsupp, orders, lineitem;

ANALYZE TABLE lineitem UPDATE HISTOGRAM ON l_returnflag, l_linestatus, l_discount, l_quantity,
  l_shipmode, l_shipinstruct, l_commitdate, l_receiptdate WITH 1024 BUCKETS;
ANALYZE TABLE orders   UPDATE HISTOGRAM ON o_orderstatus, o_orderpriority, o_comment WITH 1024 BUCKETS;
ANALYZE TABLE customer UPDATE HISTOGRAM ON c_mktsegment, c_acctbal, c_phone WITH 1024 BUCKETS;
ANALYZE TABLE part     UPDATE HISTOGRAM ON p_brand, p_type, p_size, p_container, p_name WITH 1024 BUCKETS;
ANALYZE TABLE supplier UPDATE HISTOGRAM ON s_comment WITH 1024 BUCKETS;
ANALYZE TABLE nation   UPDATE HISTOGRAM ON n_name WITH 32 BUCKETS;
ANALYZE TABLE region   UPDATE HISTOGRAM ON r_name WITH 8 BUCKETS;
