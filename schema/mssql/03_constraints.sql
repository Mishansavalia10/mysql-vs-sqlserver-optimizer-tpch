-- Foreign keys and secondary indexes, added after load. Index names and key
-- columns match schema/mysql/03_constraints.sql exactly.

CREATE INDEX idx_nation_regionkey   ON dbo.nation   (n_regionkey);
CREATE INDEX idx_supplier_nationkey ON dbo.supplier (s_nationkey);
CREATE INDEX idx_customer_nationkey ON dbo.customer (c_nationkey);
CREATE INDEX idx_partsupp_suppkey   ON dbo.partsupp (ps_suppkey);
CREATE INDEX idx_orders_custkey     ON dbo.orders   (o_custkey);
CREATE INDEX idx_orders_orderdate   ON dbo.orders   (o_orderdate);
CREATE INDEX idx_lineitem_partsupp  ON dbo.lineitem (l_partkey, l_suppkey);
CREATE INDEX idx_lineitem_suppkey   ON dbo.lineitem (l_suppkey);
CREATE INDEX idx_lineitem_shipdate  ON dbo.lineitem (l_shipdate);
GO

ALTER TABLE dbo.nation   ADD CONSTRAINT fk_nation_region    FOREIGN KEY (n_regionkey) REFERENCES dbo.region (r_regionkey);
ALTER TABLE dbo.supplier ADD CONSTRAINT fk_supplier_nation  FOREIGN KEY (s_nationkey) REFERENCES dbo.nation (n_nationkey);
ALTER TABLE dbo.customer ADD CONSTRAINT fk_customer_nation  FOREIGN KEY (c_nationkey) REFERENCES dbo.nation (n_nationkey);
ALTER TABLE dbo.partsupp ADD CONSTRAINT fk_partsupp_part    FOREIGN KEY (ps_partkey)  REFERENCES dbo.part (p_partkey);
ALTER TABLE dbo.partsupp ADD CONSTRAINT fk_partsupp_supplier FOREIGN KEY (ps_suppkey) REFERENCES dbo.supplier (s_suppkey);
ALTER TABLE dbo.orders   ADD CONSTRAINT fk_orders_customer  FOREIGN KEY (o_custkey)   REFERENCES dbo.customer (c_custkey);
ALTER TABLE dbo.lineitem ADD CONSTRAINT fk_lineitem_orders  FOREIGN KEY (l_orderkey)  REFERENCES dbo.orders (o_orderkey);
ALTER TABLE dbo.lineitem ADD CONSTRAINT fk_lineitem_partsupp FOREIGN KEY (l_partkey, l_suppkey) REFERENCES dbo.partsupp (ps_partkey, ps_suppkey);
GO
