locals {
  script_basename    = basename(var.script_file_path)
  script_name_no_ext = trimsuffix(local.script_basename, ".py")
  sql_basename       = basename(var.sql_file_path)
  handler            = var.handler != null ? var.handler : "${local.script_name_no_ext}.lambda_handler"
  role_arn           = var.create_role && var.role_arn == null ? aws_iam_role.lambda_exec_role[0].arn : var.role_arn
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.root}/.terraform/${var.function_name}.zip"

  # Package script at root
  source {
    content  = file(var.script_file_path)
    filename = local.script_basename
  }

  # Package script under bin/ directory
  source {
    content  = file(var.script_file_path)
    filename = "bin/${local.script_basename}"
  }

  # Package SQL under athena/ directory
  source {
    content  = file(var.sql_file_path)
    filename = "athena/${local.sql_basename}"
  }

  # Package SQL under bin/athena/ directory
  source {
    content  = file(var.sql_file_path)
    filename = "bin/athena/${local.sql_basename}"
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  count = var.create_role && var.role_arn == null ? 1 : 0
  name  = "${var.function_name}_role"

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

resource "aws_lambda_function" "this" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.function_name
  role             = local.role_arn
  handler          = local.handler
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = var.runtime
  timeout          = var.timeout

  dynamic "environment" {
    for_each = length(var.environment_variables) > 0 ? [1] : []
    content {
      variables = var.environment_variables
    }
  }
}
