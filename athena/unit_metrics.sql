WITH monthly_spend AS (
  SELECT 
    substr(CAST(line_item_usage_start_date AS VARCHAR), 1, 7) AS month,
    SUM(line_item_unblended_cost) AS total_cloud_cost
  FROM cur_reports
  GROUP BY 1
)
SELECT 
  s.month,
  s.total_cloud_cost,
  m.active_users,
  ROUND(s.total_cloud_cost / (m.active_users / 1000.0), 4) AS cost_per_kmau
FROM monthly_spend s
JOIN mau_telemetry m ON s.month = m.month;