variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "floci_endpoint" {
  description = "Floci / Local AWS endpoint URL"
  type        = string
  default     = "http://localhost:4566"
}

variable "data_bucket_name" {
  description = "S3 bucket name where CUR and MAU data reside (matches schema.sql LOCATION)"
  type        = string
  default     = "finops-unit-metrics"
}
