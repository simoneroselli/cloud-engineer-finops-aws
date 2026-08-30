# kMAU Cost

This function is a FinOps example for normalizing cloud spend against platform usage. It measures cost per thousand monthly active users (kMAU) so teams can understand whether infrastructure cost is rising faster than product adoption.

## Why this matters

A raw cloud bill tells you what you spent, but not whether the spend is efficient. kMAU helps connect operating costs to usage growth and provides a simple business-oriented lens for cost efficiency.

## What the Lambda does

- reads the unit metrics SQL from the packaged Athena query
- executes the query against CUR and MAU datasets
- calculates monthly total cost and cost per kMAU
- returns the cost trend as structured JSON

## Best practices captured

- correlate cloud spend with product usage, not just raw costs
- compare month-over-month cost efficiency to identify drift
- use a simple metric that business and engineering stakeholders can understand
- keep the metric anchored to actual usage data for better decision making

## Lambda name

`finops_kmau_cost_reporter`

## Related files

- [bin/kmau_cost.py](../bin/kmau_cost.py)
- [athena/unit_metrics.sql](../athena/unit_metrics.sql)
- [terraform/main.tf](../terraform/main.tf)
