# Anomaly Detection

This function is a FinOps best-practice example for spotting unusual cost spikes before they become a surprise. It runs an Athena query against CUR data and surfaces dates where spend deviates materially from the preceding period.

## Why this matters

Cloud costs are rarely flat. A successful FinOps practice focuses on early detection of unusual spend patterns so engineering and finance teams can review changes quickly.

## What the Lambda does

- reads the anomaly detection SQL from the bundled Athena query
- starts an Athena query execution
- waits for the result to finish
- parses the result set into a structured anomaly payload
- returns the flagged costs as JSON for downstream dashboards, alerts, or automation

## Best practices captured

- compare current spend to a recent baseline
- track percentage variance and magnitude of spend jumps
- alert on service-level spikes rather than only total monthly spend
- keep the query logic close to the source data so the signal is easy to explain and audit

## Lambda name

`finops_anomaly_detection_reporter`

## Related files

- [bin/anomaly_detection.py](../bin/anomaly_detection.py)
- [athena/anomaly_detection.sql](../athena/anomaly_detection.sql)
- [terraform/main.tf](../terraform/main.tf)
