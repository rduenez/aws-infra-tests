# DB Subnet Group (using public subnets for public accessibility)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.public[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# RDS MySQL Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-mysql"

  # Engine configuration
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = var.db_instance_class
  allocated_storage    = 20
  max_allocated_storage = 100
  storage_type         = "gp3"

  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # Network configuration - PUBLIC ACCESS
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = true
  port                   = 3306

  # Backup & Maintenance
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  # Other settings
  multi_az               = false
  skip_final_snapshot    = true
  deletion_protection    = false
  copy_tags_to_snapshot  = true

  # Performance Insights (free tier)
  performance_insights_enabled = false

  # Parameter group for MySQL 8.0
  parameter_group_name = aws_db_parameter_group.main.name

  tags = {
    Name = "${var.project_name}-mysql"
  }
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-mysql-params"
  family = "mysql8.0"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }

  tags = {
    Name = "${var.project_name}-mysql-params"
  }
}
