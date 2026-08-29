# --- S3 Buckets & Data Objects ---

resource "aws_s3_bucket" "finops_data" {
  bucket        = var.data_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket" "athena_results" {
  bucket        = "${var.data_bucket_name}-results"
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

# --- Athena Resources ---

resource "aws_athena_database" "finops_db" {
  name   = "finops_db"
  bucket = aws_s3_bucket.athena_results.bucket
}

resource "aws_athena_workgroup" "finops_workgroup" {
  name = "finops_workgroup"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = false

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/output/"
    }
  }
}

# --- Athena Saved Queries ---

resource "aws_athena_named_query" "schema" {
  name      = "create_finops_schemas"
  workgroup = aws_athena_workgroup.finops_workgroup.id
  database  = aws_athena_database.finops_db.name
  query     = file("${path.module}/athena/schema.sql")
}

resource "aws_athena_named_query" "unit_metrics" {
  name      = "finops_unit_metrics"
  workgroup = aws_athena_workgroup.finops_workgroup.id
  database  = aws_athena_database.finops_db.name
  query     = file("${path.module}/athena/unit_metrics.sql")
}
