import json
import os
import time

import boto3

ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", None)
athena_client = boto3.client("athena", endpoint_url=ENDPOINT_URL)


def load_sql_query() -> str:
    """Reads the SQL query from the bundled athena directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "athena", "kmau_cost.sql"),
        os.path.join(script_dir, "..", "athena", "kmau_cost.sql"),
        os.path.join(os.getcwd(), "athena", "kmau_cost.sql"),
        os.path.join(os.getcwd(), "bin", "athena", "kmau_cost.sql"),
    ]
    for sql_path in candidates:
        if os.path.exists(sql_path):
            with open(sql_path, "r") as f:
                return f.read()
    raise FileNotFoundError("Could not locate athena/unit_metrics.sql in package")


def lambda_handler(event, context):
    database = os.environ.get("ATHENA_DATABASE", "default")
    output_location = os.environ.get("RESULTS_BUCKET", "s3://finops-unit-metrics/output/")

    query_sql = load_sql_query()

    execution_response = athena_client.start_query_execution(
        QueryString=query_sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location},
    )
    query_id = execution_response["QueryExecutionId"]

    while True:
        status_response = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = status_response["QueryExecution"]["Status"]["State"]

        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        reason = status_response["QueryExecution"]["Status"].get(
            "StateChangeReason", "Unknown failure"
        )
        raise RuntimeError(f"Athena query failed with state '{state}': {reason}")

    results_response = athena_client.get_query_results(QueryExecutionId=query_id)
    rows = results_response["ResultSet"]["Rows"]

    monthly_costs = []
    for row in rows[1:]:
        cols = [col.get("VarCharValue", "") for col in row["Data"]]
        monthly_costs.append(
            {
                "month": cols[0],
                "total_cloud_cost": float(cols[1]) if cols[1] else 0.0,
                "active_users": int(float(cols[2])) if cols[2] else 0,
                "cost_per_kmau": float(cols[3]) if cols[3] else 0.0,
            }
        )

    print(f"kMAU analysis complete. Evaluated {len(monthly_costs)} monthly records.")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "query_execution_id": query_id,
                "monthly_cost_per_kmau": monthly_costs,
            }
        ),
    }
