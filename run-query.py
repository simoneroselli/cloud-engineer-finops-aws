#!/usr/bin/env python3
"""Script to ensure Glue schemas and execute Athena FinOps unit metrics query against Floci/AWS."""

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


def run_sql_file(client, file_path: str, fetch_results: bool = True):
    """Reads a SQL file and executes its statements."""
    print(f"\n--- Running: {file_path} ---")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]

    for stmt in statements:
        query_id = execute_and_wait(client, stmt)
        if fetch_results:
            print_query_results(client, query_id)


def ensure_glue_schema():
    """Registers the Glue database and tables in Floci so Athena/DuckDB can query them."""
    glue = boto3.client(
        "glue",
        endpoint_url=FLOCI_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    print(f"Ensuring Glue database '{DATABASE_NAME}' exists...")
    try:
        glue.create_database(DatabaseInput={"Name": DATABASE_NAME})
    except Exception as e:
        if "AlreadyExists" not in str(e):
            print(f"  Database note: {e}")

    # Register cur_reports
    print("Ensuring Glue table 'cur_reports' exists...")
    try:
        glue.create_table(
            DatabaseName=DATABASE_NAME,
            TableInput={
                "Name": "cur_reports",
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    "classification": "csv",
                    "skip.header.line.count": "1",
                },
                "StorageDescriptor": {
                    "Location": "s3://finops-unit-metrics/cur/",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                        "Parameters": {"field.delim": ","},
                    },
                    "Columns": [
                        {"Name": "line_item_usage_start_date", "Type": "string"},
                        {"Name": "line_item_product_code", "Type": "string"},
                        {"Name": "line_item_unblended_cost", "Type": "double"},
                    ],
                },
            },
        )
    except Exception as e:
        if "AlreadyExists" not in str(e):
            print(f"  cur_reports note: {e}")

    # Register mau_telemetry
    print("Ensuring Glue table 'mau_telemetry' exists...")
    try:
        glue.create_table(
            DatabaseName=DATABASE_NAME,
            TableInput={
                "Name": "mau_telemetry",
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    "classification": "csv",
                    "skip.header.line.count": "1",
                },
                "StorageDescriptor": {
                    "Location": "s3://finops-unit-metrics/mau/",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                        "Parameters": {"field.delim": ","},
                    },
                    "Columns": [
                        {"Name": "month", "Type": "string"},
                        {"Name": "active_users", "Type": "int"},
                    ],
                },
            },
        )
    except Exception as e:
        if "AlreadyExists" not in str(e):
            print(f"  mau_telemetry note: {e}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    unit_metrics_file = os.path.join(base_dir, "athena", "unit_metrics.sql")

    try:
        # Step 1: Ensure Glue catalog schema is registered
        ensure_glue_schema()

        # Step 2: Run unit metrics query and display results
        print(f"\nConnecting to Athena on {FLOCI_ENDPOINT} (Database: {DATABASE_NAME})")
        client = get_athena_client()
        run_sql_file(client, unit_metrics_file, fetch_results=True)

        print("Query executed successfully.")
    except Exception as e:
        print(f"Error executing queries: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
