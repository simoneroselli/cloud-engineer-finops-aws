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
