-- CUR Table Definition
CREATE EXTERNAL TABLE IF NOT EXISTS cur_reports (
  line_item_usage_start_date STRING,
  line_item_product_code STRING,
  line_item_unblended_cost DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION 's3://finops-unit-metrics/cur/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Telemetry Table Definition
CREATE EXTERNAL TABLE IF NOT EXISTS mau_telemetry (
  month STRING,
  active_users INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION 's3://finops-unit-metrics/mau/'
TBLPROPERTIES ('skip.header.line.count'='1');