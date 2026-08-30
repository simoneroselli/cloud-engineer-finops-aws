SELECT
  line_item_product_code AS aws_service,
  ROUND(SUM(line_item_unblended_cost), 2) AS total_spend,
  ROUND(
    SUM(
      CASE
        WHEN
          resource_tags_user_environment IS NULL
          OR resource_tags_user_environment = ''
          OR resource_tags_user_cost_center IS NULL
          OR resource_tags_user_cost_center = ''
          THEN line_item_unblended_cost
        ELSE 0
      END
    ), 2
  ) AS untagged_spend,
  ROUND(
    (
      SUM(
        CASE
          WHEN
            resource_tags_user_environment IS NULL
            OR resource_tags_user_environment = ''
            OR resource_tags_user_cost_center IS NULL
            OR resource_tags_user_cost_center = ''
            THEN line_item_unblended_cost
          ELSE 0
        END
      ) / SUM(line_item_unblended_cost)
    ) * 100, 2
  ) AS untagged_percentage
FROM cur_reports
GROUP BY aws_service
ORDER BY untagged_spend DESC
