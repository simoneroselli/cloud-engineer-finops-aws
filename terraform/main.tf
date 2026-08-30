# --- S3 Buckets & Data Objects ---

resource "aws_s3_bucket" "finops_data" {
  bucket        = var.data_bucket_name
  force_destroy = true
}

resource "aws_s3_object" "cur_data" {
  bucket = aws_s3_bucket.finops_data.id
  key    = "cur/cur_data.csv"
  source = "${path.module}/../data/cur_data.csv"
  etag   = filemd5("${path.module}/../data/cur_data.csv")
}

resource "aws_s3_object" "mau_data" {
  bucket = aws_s3_bucket.finops_data.id
  key    = "mau/mau_data.csv"
  source = "${path.module}/../data/mau_data.csv"
  etag   = filemd5("${path.module}/../data/mau_data.csv")
}

# --- Functions ---

module "untagged_spend" {
  source = "./modules/athena_lambda_reporter"

  function_name = "finops_untagged_spend_reporter"
  script_file_path = "${path.module}/../bin/untagged_spend.py"
  sql_file_path    = "${path.module}/../athena/untagged_spend.sql"
  handler          = "untagged_spend.lambda_handler"

  environment_variables = {
    ATHENA_DATABASE = "default"
    RESULTS_BUCKET  = "s3://${aws_s3_bucket.finops_data.bucket}/output"
  }
}

module "anomaly_detection" {
  source = "./modules/athena_lambda_reporter"

  function_name    = "finops_anomaly_detection_reporter"
  script_file_path = "${path.module}/../bin/anomaly_detection.py"
  sql_file_path    = "${path.module}/../athena/anomaly_detection.sql"
  handler          = "anomaly_detection.lambda_handler"

  environment_variables = {
    ATHENA_DATABASE = "default"
    RESULTS_BUCKET  = "s3://${aws_s3_bucket.finops_data.bucket}/output"
  }
}

module "kmau_cost" {
  source = "./modules/athena_lambda_reporter"

  function_name    = "finops_kmau_cost_reporter"
  script_file_path = "${path.module}/../bin/kmau_cost.py"
  sql_file_path    = "${path.module}/../athena/kmau_cost.sql"
  handler          = "kmau_cost.lambda_handler"

  environment_variables = {
    ATHENA_DATABASE = "default"
    RESULTS_BUCKET  = "s3://${aws_s3_bucket.finops_data.bucket}/output"
  }
}