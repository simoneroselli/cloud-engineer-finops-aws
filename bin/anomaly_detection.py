import json
import os
import time

import boto3

# Extract local endpoint URL for Floci integration
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", None)
athena_client = boto3.client("athena", endpoint_url=ENDPOINT_URL)

def load_sql_query() -> str:
    """Reads the SQL anomaly query from the bundled athena directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "athena", "anomaly_detection.sql")
    with open(sql_path, "r") as f:
        return f.read()

def lambda_handler(event, context):
    database = os.environ.get("ATHENA_DATABASE", "default")
    output_location = os.environ.get("RESULTS_BUCKET", "s3://finops-unit-metrics-results/athena-results/")
    
    query_sql = load_sql_query()
    
    # Trigger Athena execution
    execution_response = athena_client.start_query_execution(
        QueryString=query_sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location}
    )
    query_id = execution_response["QueryExecutionId"]
    
    # Wait for execution state
    while True:
        status_response = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = status_response["QueryExecution"]["Status"]["State"]
        
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)
        
    if state != "SUCCEEDED":
        reason = status_response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown failure")
        raise RuntimeError(f"Athena query failed with state '{state}': {reason}")
        
    # Fetch result set
    results_response = athena_client.get_query_results(QueryExecutionId=query_id)
    rows = results_response["ResultSet"]["Rows"]
    
    anomalies = []
    # Skip header row (index 0)
    for row in rows[1:]:
        cols = [col.get("VarCharValue", "") for col in row["Data"]]
        anomalies.append({
            "usage_date": cols[0],
            "aws_service": cols[1],
            "daily_cost": float(cols[2]) if cols[2] else 0.0,
            "prev_day_cost": float(cols[3]) if cols[3] else 0.0,
            "cost_difference": float(cols[4]) if cols[4] else 0.0,
            "percentage_variance": float(cols[5]) if cols[5] else 0.0
        })
        
    print(f"Anomaly Detection Complete. Flagged {len(anomalies)} spending spikes.")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "query_execution_id": query_id,
            "detected_anomalies_count": len(anomalies),
            "anomalies": anomalies
        })
    }