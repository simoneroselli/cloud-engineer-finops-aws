WITH monthly_spend AS (
  SELECT
    SUBSTR(line_item_usage_start_date, 1, 7) AS billing_month,
    SUM(line_item_unblended_cost) AS total_cloud_cost
  FROM cur_reports
  GROUP BY SUBSTR(line_item_usage_start_date, 1, 7)
)

SELECT
  s.billing_month,
  s.total_cloud_cost,
  m.active_users,
  ROUND(s.total_cloud_cost / (m.active_users / 1000.0), 4) AS cost_per_kmau
FROM monthly_spend AS s
INNER JOIN mau_telemetry AS m ON s.billing_month = m.month
