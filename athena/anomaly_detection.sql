WITH daily_spend AS (
  SELECT
    line_item_usage_start_date AS usage_date,
    line_item_product_code AS aws_service,
    ROUND(SUM(line_item_unblended_cost), 2) AS daily_cost
  FROM cur_reports
  GROUP BY usage_date, aws_service
),

spend_with_lag AS (
  SELECT
    usage_date,
    aws_service,
    daily_cost,
    LAG(daily_cost) OVER (
      PARTITION BY aws_service
      ORDER BY usage_date
    ) AS prev_day_cost
  FROM daily_spend
)

SELECT
  usage_date,
  aws_service,
  daily_cost,
  COALESCE(prev_day_cost, 0.0) AS prev_day_cost,
  ROUND(daily_cost - COALESCE(prev_day_cost, 0.0), 2) AS cost_difference,
  CASE
    WHEN prev_day_cost IS NULL OR prev_day_cost = 0 THEN 0.0
    ELSE ROUND(((daily_cost - prev_day_cost) / prev_day_cost) * 100, 2)
  END AS percentage_variance
FROM spend_with_lag
WHERE
  prev_day_cost IS NOT NULL
  AND (daily_cost - prev_day_cost) > 50.0
ORDER BY cost_difference DESC
