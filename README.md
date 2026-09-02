# Cloud Engineer FinOps AWS

A practical FinOps starter project for running cost visibility, governance, and anomaly-detection workloads locally with Terraform, Athena, and Lambda-style Python functions.

This repository packages a few representative AWS cost-optimization checks as examples you can adapt for real cloud operations: anomaly detection, kMAU cost analysis, and untagged spend reporting.

## Functions

- [Anomaly Detection](doc/anomaly-detection.md) — detect unusual spend spikes and identify service-level cost anomalies.
- [kMAU Cost](doc/kmau-cost.md) — measure monthly cost per thousand active users to understand efficiency trends.
- [Untagged Resources](doc/untagged-spend.md) — highlight spend that is not properly attributed to a team or application.

## Getting Started

```bash
# clone the repository
git clone https://github.com/simoneroselli/cloud-engineer-finops-aws.git

# start local AWS-compatible emulation and the Terraform CLI container
cd /path/to/cloud-engineer-finops-aws
docker compose up -d

# run Terraform from inside the container (no local install required)
docker compose exec terraform terraform init
docker compose exec terraform terraform apply
```

## Local Trivy policy check

```bash
docker compose run --rm trivy config --config-check /root/.trivy/policies --check-namespaces user --exit-code 1 .
```

This runs Trivy inside the project container against the mounted Terraform config and validates the custom policy rules stored under the repository's `.trivy` directory.

## Execute Lambdas

```bash
aws --endpoint-url=http://localhost:4566 lambda invoke \
  --function-name finops_kmau_cost_reporter \
  --cli-binary-format raw-in-base64-out \
  --payload '{}' \
  response.json
```

The project is intentionally designed as a simple FinOps reference pattern: local AWS emulation for development, Athena for SQL-based analysis, Python Lambda handlers for logic, and Terraform for repeatable deployment.
