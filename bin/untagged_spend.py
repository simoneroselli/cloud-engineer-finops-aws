import json
import os
import time
import boto3

# Support local Floci testing endpoint if defined
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", None)
athena_client = boto3.client("athena", endpoint_url=ENDPOINT_URL)

def load_sql_query() -> str:
    """Reads the SQL query from the bundled athena directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "athena", "untagged_spend.sql"),
        os.path.join(script_dir, "..", "athena", "untagged_spend.sql"),
        os.path.join(os.getcwd(), "athena", "untagged_spend.sql"),
        os.path.join(os.getcwd(), "bin", "athena", "untagged_spend.sql"),
    ]
    for sql_path in candidates:
        if os.path.exists(sql_path):
            with open(sql_path, "r") as f:
                return f.read()
    raise FileNotFoundError("Could not locate athena/untagged_spend.sql in package")

def lambda_handler(event, context):
    database = os.environ.get("ATHENA_DATABASE", "default")
    output_location = os.environ.get("RESULTS_BUCKET", "s3://finops-unit-metrics/output/")
    
    # 1. Read query string from file
    query_sql = load_sql_query()
    
    # 2. Trigger asynchronous query execution
    execution_response = athena_client.start_query_execution(
        QueryString=query_sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location}
    )
    query_id = execution_response["QueryExecutionId"]
    
    # 3. Poll until query reaches terminal state
    while True:
        status_response = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = status_response["QueryExecution"]["Status"]["State"]
        
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)
        
    if state != "SUCCEEDED":
        reason = status_response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown failure")
        raise RuntimeError(f"Athena query failed with state '{state}': {reason}")
        
    # 4. Retrieve execution result set
    results_response = athena_client.get_query_results(QueryExecutionId=query_id)
    rows = results_response["ResultSet"]["Rows"]
    
    parsed_metrics = []
    # Skip CSV header row (index 0)
    for row in rows[1:]:
        cols = [col.get("VarCharValue", "") for col in row["Data"]]
        parsed_metrics.append({
            "aws_service": cols[0],
            "total_spend": float(cols[1]) if cols[1] else 0.0,
            "untagged_spend": float(cols[2]) if cols[2] else 0.0,
            "untagged_percentage": float(cols[3]) if cols[3] else 0.0
        })
        
    # 5. Filter for non-compliant services exceeding 0% untagged spend
    non_compliant = [m for m in parsed_metrics if m["untagged_percentage"] > 0]
    
    print(f"Analysis Complete. Identified {len(non_compliant)} services with unallocated spend.")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "query_execution_id": query_id,
            "services_analyzed": len(parsed_metrics),
            "non_compliant_services": non_compliant
        })
    }