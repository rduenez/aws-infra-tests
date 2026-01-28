# SQS Queue for async create operations
resource "aws_sqs_queue" "create_queue" {
  name                       = "${var.project_name}-create-queue"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 60

  tags = {
    Name = "${var.project_name}-create-queue"
  }
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-create-dlq"
  message_retention_seconds = 1209600  # 14 days

  tags = {
    Name = "${var.project_name}-create-dlq"
  }
}

# Redrive policy - send failed messages to DLQ
resource "aws_sqs_queue_redrive_policy" "main" {
  queue_url = aws_sqs_queue.create_queue.id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}
