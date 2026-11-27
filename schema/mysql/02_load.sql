-- Bulk load dbgen output. {data_dir} is substituted by harness/load.py with the
-- client-side directory (LOCAL INFILE streams the file over the connection).
SET SESSION foreign_key_checks = 0;
SET SESSION unique_checks = 0;

LOAD DATA LOCAL INFILE '{data_dir}/region.tbl'   INTO TABLE region   FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/nation.tbl'   INTO TABLE nation   FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/supplier.tbl' INTO TABLE supplier FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/customer.tbl' INTO TABLE customer FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/part.tbl'     INTO TABLE part     FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/partsupp.tbl' INTO TABLE partsupp FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/orders.tbl'   INTO TABLE orders   FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
LOAD DATA LOCAL INFILE '{data_dir}/lineitem.tbl' INTO TABLE lineitem FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';

SET SESSION foreign_key_checks = 1;
SET SESSION unique_checks = 1;
