#!/usr/bin/env python3
"""Script to execute Athena schema setup and unit metrics queries against Floci/AWS."""

import os
import sys
import time
import boto3

FLOCI_ENDPOINT = os.getenv("FLOCI_ENDPOINT", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "mock")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mock")
DATABASE_NAME = os.getenv("ATHENA_DATABASE", "default")
RESULTS_OUTPUT_LOCATION = os.getenv(
    "ATHENA_OUTPUT_LOCATION", "s3://finops-unit-metrics/output/"
)


def get_athena_client():
    return boto3.client(
        "athena",
        endpoint_url=FLOCI_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def execute_and_wait(client, query_string: str, database: str = DATABASE_NAME) -> str:
    """Submits a query to Athena and polls until it reaches a terminal state."""
    response = client.start_query_execution(
        QueryString=query_string,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": RESULTS_OUTPUT_LOCATION},
    )
    query_id = response["QueryExecutionId"]
    print(f"Submitted query (ID: {query_id}). Waiting for completion...")

    while True:
        execution = client.get_query_execution(QueryExecutionId=query_id)
        status = execution["QueryExecution"]["Status"]["State"]

        if status == "SUCCEEDED":
            print(f"Query {query_id} SUCCEEDED.")
            return query_id
        elif status in ["FAILED", "CANCELLED"]:
            reason = execution["QueryExecution"]["Status"].get(
                "StateChangeReason", "Unknown reason"
            )
            raise RuntimeError(f"Query {query_id} {status}: {reason}")

        time.sleep(1)


def print_query_results(client, query_id: str):
    """Fetches and prints query results in a clean tabular format."""
    paginator = client.get_paginator("get_query_results")
    for page in paginator.paginate(QueryExecutionId=query_id):
        rows = page["ResultSet"]["Rows"]
        if not rows:
            print("No results returned.")
            return

        # Extract headers and rows
        headers = [col.get("VarCharValue", "") for col in rows[0]["Data"]]
        col_widths = [len(h) for h in headers]

        data_rows = []
        for row in rows[1:]:
            values = [col.get("VarCharValue", "") for col in row["Data"]]
            data_rows.append(values)
            for idx, val in enumerate(values):
                col_widths[idx] = max(col_widths[idx], len(val))

        header_fmt = " | ".join(f"{{:<{col_widths[i]}}}" for i in range(len(headers)))
        separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

        print("\n" + header_fmt.format(*headers))
        print(separator)
        for data in data_rows:
            print(header_fmt.format(*data))
        print()


def run_sql_file(client, file_path: str, fetch_results: bool = False):
    """Reads a SQL file and executes its statements."""
    print(f"\n--- Running: {file_path} ---")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split multiple statements if any (e.g., schema.sql with multiple CREATE TABLE)
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]

    for stmt in statements:
        query_id = execute_and_wait(client, stmt)
        if fetch_results:
            print_query_results(client, query_id)


def main():
    print(f"Connecting to Athena on {FLOCI_ENDPOINT} (Database: {DATABASE_NAME})")
    client = get_athena_client()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_file = os.path.join(base_dir, "athena", "schema.sql")
    unit_metrics_file = os.path.join(base_dir, "athena", "unit_metrics.sql")

    try:
        # Step 1: Run table creation schemas
        run_sql_file(client, schema_file, fetch_results=False)

        # Step 2: Run unit metrics query and display results
        run_sql_file(client, unit_metrics_file, fetch_results=True)

        print("All queries executed successfully.")
    except Exception as e:
        print(f"Error executing queries: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
