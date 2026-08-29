output "data_bucket" {
  description = "S3 bucket containing the CUR and MAU source datasets"
  value       = aws_s3_bucket.finops_data.bucket
}

output "results_bucket" {
  description = "S3 bucket configured for Athena query results"
  value       = aws_s3_bucket.athena_results.bucket
}

output "athena_database" {
  description = "Athena database name"
  value       = aws_athena_database.finops_db.name
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = "primary"
}

output "named_query_schema_id" {
  description = "Athena named query ID for schema creation"
  value       = aws_athena_named_query.schema.id
}

output "named_query_unit_metrics_id" {
  description = "Athena named query ID for unit metrics calculation"
  value       = aws_athena_named_query.unit_metrics.id
}
