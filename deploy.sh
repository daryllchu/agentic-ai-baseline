#!/bin/bash

# HR Data Exchange Hub Deployment Script
set -e

# Configuration
STACK_NAME="hr-data-hub-prod"
REGION="us-east-1"
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)

echo "🚀 Deploying HR Data Exchange Hub..."

# 1. Deploy AWS Infrastructure
echo "📦 Deploying AWS infrastructure..."
aws cloudformation deploy \
  --template-file infrastructure/aws-infrastructure.yml \
  --stack-name $STACK_NAME \
  --parameter-overrides \
    Environment=prod \
    DBPassword=$DB_PASSWORD \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# 2. Get infrastructure outputs
echo "📋 Getting infrastructure details..."
VPC_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`VPCId`].OutputValue' --output text --region $REGION)
DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' --output text --region $REGION)
S3_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' --output text --region $REGION)

# 3. Create production environment file
echo "⚙️ Creating production configuration..."
cat > backend/.env.prod << EOF
DATABASE_URL=postgresql://postgres:$DB_PASSWORD@$DB_ENDPOINT:5432/hr_data_hub
REDIS_URL=redis://localhost:6379
S3_BUCKET_NAME=$S3_BUCKET
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com
EOF

# 4. Build and push Docker image
echo "🐳 Building Docker image..."
cd backend
docker build -t hr-data-hub:latest .

# 5. Create ECS task definition
echo "📝 Creating ECS configuration..."
cat > task-definition.json << EOF
{
  "family": "hr-data-hub",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "hr-data-hub-api",
      "image": "hr-data-hub:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://postgres:$DB_PASSWORD@$DB_ENDPOINT:5432/hr_data_hub"},
        {"name": "S3_BUCKET_NAME", "value": "$S3_BUCKET"},
        {"name": "SECRET_KEY", "value": "$SECRET_KEY"},
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hr-data-hub",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

echo "✅ Deployment configuration complete!"
echo "📊 Infrastructure Details:"
echo "  VPC ID: $VPC_ID"
echo "  Database: $DB_ENDPOINT"
echo "  S3 Bucket: $S3_BUCKET"
echo ""
echo "🔐 Credentials saved to backend/.env.prod"
echo "⚠️  Store DB_PASSWORD securely: $DB_PASSWORD"
echo ""
echo "🚀 Next steps:"
echo "  1. Push Docker image to ECR"
echo "  2. Create ECS service"
echo "  3. Configure domain and SSL"