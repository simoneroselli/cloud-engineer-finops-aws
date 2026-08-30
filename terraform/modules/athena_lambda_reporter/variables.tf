variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "script_file_path" {
  description = "Path to the Python script file to package and execute"
  type        = string
}

variable "sql_file_path" {
  description = "Path to the SQL file to package alongside the Lambda function"
  type        = string
}

variable "handler" {
  description = "Lambda function handler string (defaults to <script_basename>.lambda_handler)"
  type        = string
  default     = null
}

variable "runtime" {
  description = "Lambda execution runtime"
  type        = string
  default     = "python3.11"
}

variable "timeout" {
  description = "Lambda execution timeout in seconds"
  type        = number
  default     = 30
}

variable "environment_variables" {
  description = "Map of environment variables to configure for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "create_role" {
  description = "Whether to create a default IAM execution role for the Lambda function"
  type        = bool
  default     = true
}

variable "role_arn" {
  description = "Existing IAM role ARN to attach to the Lambda function if create_role is false"
  type        = string
  default     = null
}
