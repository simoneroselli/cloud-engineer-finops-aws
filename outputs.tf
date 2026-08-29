output "data_bucket" {
  description = "S3 bucket containing source datasets and query results"
  value       = aws_s3_bucket.finops_data.bucket
}

output "athena_output_location" {
  description = "S3 URI configured for Athena query results"
  value       = "s3://${aws_s3_bucket.finops_data.bucket}/output/"
}



