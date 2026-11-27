-- Bulk load dbgen output. BULK INSERT reads files on the *server*, so
-- {data_dir} is the path as the SQL Server process sees it (e.g. /data/sf1 when
-- ./data is mounted at /data as in docker-compose.yml).
-- TABLOCK enables minimally logged loads under the SIMPLE recovery model.

ALTER DATABASE CURRENT SET RECOVERY SIMPLE;
GO
BULK INSERT dbo.region   FROM '{data_dir}/region.tbl'   WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.nation   FROM '{data_dir}/nation.tbl'   WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.supplier FROM '{data_dir}/supplier.tbl' WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.customer FROM '{data_dir}/customer.tbl' WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.part     FROM '{data_dir}/part.tbl'     WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.partsupp FROM '{data_dir}/partsupp.tbl' WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.orders   FROM '{data_dir}/orders.tbl'   WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK);
BULK INSERT dbo.lineitem FROM '{data_dir}/lineitem.tbl' WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', TABLOCK, BATCHSIZE = 1000000);
GO
