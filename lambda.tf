# Lambda Layer for pymysql dependency
resource "aws_lambda_layer_version" "pymysql" {
  filename            = "${path.module}/layers/pymysql.zip"
  layer_name          = "${var.project_name}-pymysql-layer"
  compatible_runtimes = ["python3.11", "python3.12"]
  description         = "PyMySQL library for MySQL database access"

  depends_on = [null_resource.create_pymysql_layer]
}

# Create pymysql layer zip
resource "null_resource" "create_pymysql_layer" {
  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${path.module}/layers/python
      pip install pymysql -t ${path.module}/layers/python --quiet
      cd ${path.module}/layers && zip -r pymysql.zip python
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

# Common Lambda environment variables
locals {
  lambda_environment = {
    DB_HOST     = aws_db_instance.main.address
    DB_USER     = var.db_username
    DB_PASSWORD = var.db_password
    DB_NAME     = var.db_name
  }

  lambda_vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
}

# =============================================================================
# Lambda: CREATE (Direct DB)
# =============================================================================
data "archive_file" "lambda_create" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/create"
  output_path = "${path.module}/.terraform/tmp/lambda_create.zip"
}

resource "aws_lambda_function" "create" {
  function_name    = "${var.project_name}-create"
  filename         = data.archive_file.lambda_create.output_path
  source_code_hash = data.archive_file.lambda_create.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 256

  layers = [aws_lambda_layer_version.pymysql.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]
}

# =============================================================================
# Lambda: READ (Direct DB)
# =============================================================================
data "archive_file" "lambda_read" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/read"
  output_path = "${path.module}/.terraform/tmp/lambda_read.zip"
}

resource "aws_lambda_function" "read" {
  function_name    = "${var.project_name}-read"
  filename         = data.archive_file.lambda_read.output_path
  source_code_hash = data.archive_file.lambda_read.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 256

  layers = [aws_lambda_layer_version.pymysql.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]
}

# =============================================================================
# Lambda: UPDATE (Direct DB)
# =============================================================================
data "archive_file" "lambda_update" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/update"
  output_path = "${path.module}/.terraform/tmp/lambda_update.zip"
}

resource "aws_lambda_function" "update" {
  function_name    = "${var.project_name}-update"
  filename         = data.archive_file.lambda_update.output_path
  source_code_hash = data.archive_file.lambda_update.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 256

  layers = [aws_lambda_layer_version.pymysql.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]
}

# =============================================================================
# Lambda: DELETE (Direct DB)
# =============================================================================
data "archive_file" "lambda_delete" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/delete"
  output_path = "${path.module}/.terraform/tmp/lambda_delete.zip"
}

resource "aws_lambda_function" "delete" {
  function_name    = "${var.project_name}-delete"
  filename         = data.archive_file.lambda_delete.output_path
  source_code_hash = data.archive_file.lambda_delete.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 256

  layers = [aws_lambda_layer_version.pymysql.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]
}

# =============================================================================
# Lambda: SQS Producer (sends to queue)
# =============================================================================
data "archive_file" "lambda_sqs_producer" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/sqs_producer"
  output_path = "${path.module}/.terraform/tmp/lambda_sqs_producer.zip"
}

resource "aws_lambda_function" "sqs_producer" {
  function_name    = "${var.project_name}-sqs-producer"
  filename         = data.archive_file.lambda_sqs_producer.output_path
  source_code_hash = data.archive_file.lambda_sqs_producer.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 128

  environment {
    variables = {
      SQS_QUEUE_URL = aws_sqs_queue.create_queue.url
    }
  }
}

# =============================================================================
# Lambda: SQS Consumer (processes queue, writes to DB)
# =============================================================================
data "archive_file" "lambda_sqs_consumer" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/sqs_consumer"
  output_path = "${path.module}/.terraform/tmp/lambda_sqs_consumer.zip"
}

resource "aws_lambda_function" "sqs_consumer" {
  function_name    = "${var.project_name}-sqs-consumer"
  filename         = data.archive_file.lambda_sqs_consumer.output_path
  source_code_hash = data.archive_file.lambda_sqs_consumer.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 60
  memory_size      = 256

  layers = [aws_lambda_layer_version.pymysql.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]
}

# SQS Trigger for Consumer Lambda
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.create_queue.arn
  function_name    = aws_lambda_function.sqs_consumer.arn
  batch_size       = 10
  enabled          = true
}

# =============================================================================
# Lambda: SQS Consumer ORM (NOT connected to events)
# =============================================================================
# NOTE: This Lambda uses SQLAlchemy ORM instead of raw SQL.
# It is NOT automatically triggered by SQS - manual invocation only.

resource "aws_lambda_layer_version" "sqlalchemy" {
  filename            = "${path.module}/layers/sqlalchemy.zip"
  layer_name          = "${var.project_name}-sqlalchemy-layer"
  compatible_runtimes = ["python3.11", "python3.12"]
  description         = "SQLAlchemy and PyMySQL libraries for ORM-based database access"

  depends_on = [null_resource.create_sqlalchemy_layer]
}

resource "null_resource" "create_sqlalchemy_layer" {
  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${path.module}/layers/sqlalchemy_python
      pip install sqlalchemy pymysql -t ${path.module}/layers/sqlalchemy_python/python --quiet
      cd ${path.module}/layers/sqlalchemy_python && zip -r ../sqlalchemy.zip python
      rm -rf ${path.module}/layers/sqlalchemy_python
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

data "archive_file" "lambda_sqs_consumer_orm" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/sqs_consumer_orm"
  output_path = "${path.module}/.terraform/tmp/lambda_sqs_consumer_orm.zip"
}

resource "aws_lambda_function" "sqs_consumer_orm" {
  function_name    = "${var.project_name}-sqs-consumer-orm"
  filename         = data.archive_file.lambda_sqs_consumer_orm.output_path
  source_code_hash = data.archive_file.lambda_sqs_consumer_orm.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda.arn
  timeout          = 60
  memory_size      = 256

  layers = [aws_lambda_layer_version.sqlalchemy.arn]

  vpc_config {
    subnet_ids         = local.lambda_vpc_config.subnet_ids
    security_group_ids = local.lambda_vpc_config.security_group_ids
  }

  environment {
    variables = local.lambda_environment
  }

  depends_on = [aws_db_instance.main]

  tags = {
    Name        = "${var.project_name}-sqs-consumer-orm"
    Description = "ORM-based SQS consumer - NOT auto-triggered"
  }
}

# NOTE: No aws_lambda_event_source_mapping for this Lambda
# It must be invoked manually or connected to events separately if needed

# =============================================================================
# Lambda Function URLs (for easy testing)
# =============================================================================
resource "aws_lambda_function_url" "create" {
  function_name      = aws_lambda_function.create.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_function_url" "read" {
  function_name      = aws_lambda_function.read.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_function_url" "update" {
  function_name      = aws_lambda_function.update.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_function_url" "delete" {
  function_name      = aws_lambda_function.delete.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_function_url" "sqs_producer" {
  function_name      = aws_lambda_function.sqs_producer.function_name
  authorization_type = "NONE"
}
