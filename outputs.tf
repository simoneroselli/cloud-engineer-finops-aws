output "data_bucket" {
  description = "S3 bucket containing the CUR and MAU source datasets"
  value       = aws_s3_bucket.finops_data.bucket
}

output "results_bucket" {
  description = "S3 bucket configured for Athena query results"
  value       = aws_s3_bucket.athena_results.bucket
}



