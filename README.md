# FinOps Athena Lambda Reference

A practical FinOps starter project for running cost visibility, governance, and anomaly-detection workloads locally with Terraform, Athena, and Lambda-style Python functions.

This repository packages a few representative AWS cost-optimization checks as examples you can adapt for real cloud operations: anomaly detection, kMAU cost analysis, and untagged spend reporting.

## Functions

- [Anomaly Detection](doc/anomaly-detection.md) — detect unusual spend spikes and identify service-level cost anomalies.
- [kMAU Cost](doc/kmau-cost.md) — measure monthly cost per thousand active users to understand efficiency trends.
- [Untagged Resources](doc/untagged-spend.md) — highlight spend that is not properly attributed to a team or application.

## Getting Started

```bash
git clone <repo>

# start local AWS-compatible emulation
docker run --rm -p 4566:4566 -v /var/run/docker.sock:/var/run/docker.sock floci/floci:latest

# deploy the example infrastructure
cd terraform
terraform init
terraform apply
```

## Execute Lambdas

```bash
aws --endpoint-url=http://localhost:4566 lambda invoke \
  --function-name finops_kmau_cost_reporter \
  --cli-binary-format raw-in-base64-out \
  --payload '{}' \
  response.json
```

The project is intentionally designed as a simple FinOps reference pattern: local AWS emulation for development, Athena for SQL-based analysis, Python Lambda handlers for logic, and Terraform for repeatable deployment.
