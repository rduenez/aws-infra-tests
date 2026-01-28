#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CRUD App Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: terraform is not installed${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: aws cli is not installed${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}All prerequisites met!${NC}"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${RED}Error: terraform.tfvars not found${NC}"
    echo -e "Please copy terraform.tfvars.example to terraform.tfvars and configure it"
    exit 1
fi

# Step 1: Initialize Terraform
echo -e "\n${YELLOW}Step 1: Initializing Terraform...${NC}"
terraform init

# Step 2: Plan and Apply Infrastructure
echo -e "\n${YELLOW}Step 2: Planning infrastructure changes...${NC}"
terraform plan -out=tfplan

echo -e "\n${YELLOW}Do you want to apply these changes? (yes/no)${NC}"
read -r APPLY_CONFIRM

if [ "$APPLY_CONFIRM" != "yes" ]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Applying infrastructure...${NC}"
terraform apply tfplan
rm -f tfplan

# Step 3: Get ECR repository URL
echo -e "\n${YELLOW}Step 3: Getting ECR repository URL...${NC}"
ECR_REPO=$(terraform output -raw ecr_repository_url)
AWS_REGION=$(terraform output -raw 2>/dev/null aws_region || echo "us-east-1")

# Extract registry URL (without repo name)
ECR_REGISTRY=$(echo $ECR_REPO | cut -d'/' -f1)

echo -e "ECR Repository: ${GREEN}$ECR_REPO${NC}"

# Step 4: Build Docker image
echo -e "\n${YELLOW}Step 4: Building Docker image...${NC}"
cd api
docker build -t crud-app-api:latest .
cd ..

# Step 5: Login to ECR
echo -e "\n${YELLOW}Step 5: Logging into ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Step 6: Tag and push image
echo -e "\n${YELLOW}Step 6: Tagging and pushing image to ECR...${NC}"
docker tag crud-app-api:latest $ECR_REPO:latest
docker push $ECR_REPO:latest

# Step 7: Force new deployment
echo -e "\n${YELLOW}Step 7: Forcing new ECS deployment...${NC}"
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)

aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region $AWS_REGION > /dev/null

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Output useful information
echo -e "\n${YELLOW}Useful Information:${NC}"
echo -e "API Endpoint: ${GREEN}$(terraform output -raw api_endpoint)${NC}"
echo -e "ALB DNS: ${GREEN}$(terraform output -raw alb_dns_name)${NC}"
echo -e "RDS Endpoint: ${GREEN}$(terraform output -raw rds_endpoint)${NC}"

echo -e "\n${YELLOW}API Endpoints:${NC}"
echo -e "  POST   /items  - Create item"
echo -e "  GET    /items  - List items"
echo -e "  GET    /items?id=1 - Get item by ID"
echo -e "  PUT    /items  - Update item"
echo -e "  DELETE /items  - Delete item"
echo -e "  POST   /queue  - Queue create operation"
echo -e "  GET    /health - Health check"

echo -e "\n${YELLOW}Note: The ECS service may take a few minutes to become healthy.${NC}"
echo -e "Monitor the deployment with:"
echo -e "  aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION"
