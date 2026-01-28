# =============================================================================
# RDS Outputs
# =============================================================================
output "rds_endpoint" {
  description = "RDS instance endpoint (use this in DBeaver)"
  value       = aws_db_instance.main.endpoint
}

output "rds_hostname" {
  description = "RDS instance hostname"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "rds_database_name" {
  description = "Database name"
  value       = var.db_name
}

# =============================================================================
# Lambda Function URLs
# =============================================================================
output "lambda_url_create" {
  description = "Lambda URL for CREATE operation (direct DB)"
  value       = aws_lambda_function_url.create.function_url
}

output "lambda_url_read" {
  description = "Lambda URL for READ operation"
  value       = aws_lambda_function_url.read.function_url
}

output "lambda_url_update" {
  description = "Lambda URL for UPDATE operation"
  value       = aws_lambda_function_url.update.function_url
}

output "lambda_url_delete" {
  description = "Lambda URL for DELETE operation"
  value       = aws_lambda_function_url.delete.function_url
}

output "lambda_url_sqs_producer" {
  description = "Lambda URL for SQS Producer (async CREATE)"
  value       = aws_lambda_function_url.sqs_producer.function_url
}

# =============================================================================
# SQS Outputs
# =============================================================================
output "sqs_queue_url" {
  description = "SQS Queue URL"
  value       = aws_sqs_queue.create_queue.url
}

output "sqs_queue_arn" {
  description = "SQS Queue ARN"
  value       = aws_sqs_queue.create_queue.arn
}

# =============================================================================
# Connection Info
# =============================================================================
output "dbeaver_connection_info" {
  description = "Connection details for DBeaver"
  value = <<-EOT

    ============================================
    DBeaver Connection Details
    ============================================
    Host:     ${aws_db_instance.main.address}
    Port:     ${aws_db_instance.main.port}
    Database: ${var.db_name}
    Username: ${var.db_username}
    Password: (use the value from db_password variable)

    JDBC URL: jdbc:mysql://${aws_db_instance.main.endpoint}/${var.db_name}
    ============================================

  EOT
}

# =============================================================================
# ECS/ALB Outputs
# =============================================================================
output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.api.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name (API endpoint)"
  value       = aws_lb.main.dns_name
}

output "api_endpoint" {
  description = "Full API endpoint URL"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.api.name
}
