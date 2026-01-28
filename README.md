# AWS CRUD Application with Terraform

This project deploys a complete CRUD application infrastructure on AWS using Terraform.

## Architecture

- **VPC** with public and private subnets, NAT Gateway, and Internet Gateway
- **RDS MySQL** database (publicly accessible for DBeaver)
- **6 Lambda Functions**:
  - `create` - Direct CREATE operation to database
  - `read` - READ operation from database
  - `update` - UPDATE operation to database
  - `delete` - DELETE operation from database
  - `sqs-producer` - Sends create requests to SQS queue
  - `sqs-consumer` - Processes SQS messages and writes to database
- **SQS Queue** with Dead Letter Queue for async operations

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Python 3.11+ (for Lambda layer creation)
- pip (Python package manager)

## Quick Start

1. **Copy and configure variables:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init
   ```

3. **Review the plan:**
   ```bash
   terraform plan
   ```

4. **Deploy:**
   ```bash
   terraform apply
   ```

5. **Initialize the database:**
   - Connect to RDS using DBeaver with the output credentials
   - Run `init_database.sql` to create the sample table

## Lambda Function Usage

### Direct CRUD Operations

**CREATE:**
```bash
curl -X POST "$(terraform output -raw lambda_url_create)" \
  -H "Content-Type: application/json" \
  -d '{"table": "items", "data": {"name": "New Item", "description": "A new item", "price": 29.99, "quantity": 10}}'
```

**READ (all):**
```bash
curl "$(terraform output -raw lambda_url_read)?table=items"
```

**READ (by ID):**
```bash
curl "$(terraform output -raw lambda_url_read)?table=items&id=1"
```

**UPDATE:**
```bash
curl -X POST "$(terraform output -raw lambda_url_update)" \
  -H "Content-Type: application/json" \
  -d '{"table": "items", "id": 1, "data": {"name": "Updated Name", "price": 39.99}}'
```

**DELETE:**
```bash
curl -X POST "$(terraform output -raw lambda_url_delete)" \
  -H "Content-Type: application/json" \
  -d '{"table": "items", "id": 1}'
```

### Async CREATE via SQS

**Send to queue:**
```bash
curl -X POST "$(terraform output -raw lambda_url_sqs_producer)" \
  -H "Content-Type: application/json" \
  -d '{"table": "items", "data": {"name": "Async Item", "description": "Created via SQS"}}'
```

The SQS consumer Lambda will automatically process the message and write to the database.

## DBeaver Connection

After deployment, use the following connection details:
- **Host:** `terraform output -raw rds_hostname`
- **Port:** 3306
- **Database:** cruddb
- **Username:** admin
- **Password:** (your configured password)

## Cleanup

```bash
terraform destroy
```

## Security Notes

- The database is publicly accessible by default (for development/testing)
- For production, restrict `allowed_ip` to your specific IP address
- Lambda function URLs are unauthenticated for simplicity
- Database credentials should be stored in AWS Secrets Manager for production
