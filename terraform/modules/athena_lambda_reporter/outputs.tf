output "lambda_arn" {
  description = "ARN of the deployed Lambda function"
  value       = aws_lambda_function.this.arn
}

output "lambda_function_name" {
  description = "Name of the deployed Lambda function"
  value       = aws_lambda_function.this.function_name
}

output "lambda_role_arn" {
  description = "ARN of the IAM role used by the Lambda function"
  value       = local.role_arn
}
