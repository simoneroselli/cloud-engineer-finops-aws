# --- S3 Buckets & Data Objects ---

resource "aws_s3_bucket" "finops_data" {
  bucket        = var.data_bucket_name
  force_destroy = true
}

resource "aws_s3_object" "cur_data" {
  bucket = aws_s3_bucket.finops_data.id
  key    = "cur/cur_data.csv"
  source = "${path.module}/data/cur_data.csv"
  etag   = filemd5("${path.module}/data/cur_data.csv")
}

resource "aws_s3_object" "mau_data" {
  bucket = aws_s3_bucket.finops_data.id
  key    = "mau/mau_data.csv"
  source = "${path.module}/data/mau_data.csv"
  etag   = filemd5("${path.module}/data/mau_data.csv")
}

# --- Lambda Functions: Untagged Spend ---

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/untagged_spend.zip"

  # Include python script and SQL directory in zip payload
  source {
    content  = file("${path.module}/bin/untagged_spend.py")
    filename = "bin/untagged_spend.py"
  }

  source {
    content  = file("${path.module}/athena/untagged_spend.sql")
    filename = "athena/untagged_spend.sql"
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "finops_untagged_spend_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_lambda_function" "finops_untagged_spend" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "finops_untagged_spend_reporter"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "untagged_spend.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30

  environment {
    variables = {
      ATHENA_DATABASE = "default"
      RESULTS_BUCKET  = "s3://finops-unit-metrics/output"
    }
  }
}