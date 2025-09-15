# HR Data Exchange Hub - Deployment Guide

## Quick Deploy (Windows)

```bash
# 1. Deploy infrastructure and backend
.\deploy.bat

# 2. Run database migrations
cd backend
.\migrate-prod.bat

# 3. Build and deploy frontend
cd ..\frontend
npm run build
```

## Prerequisites

### AWS Setup
- AWS CLI configured with appropriate permissions
- Docker installed and running
- Node.js 18+ for frontend build

### Required AWS Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "ec2:*",
        "rds:*",
        "s3:*",
        "ecs:*",
        "ecr:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Deployment Steps

### 1. Infrastructure Deployment
```bash
# Deploy AWS resources
.\deploy.bat
```

This creates:
- VPC with public/private subnets
- RDS PostgreSQL database
- S3 bucket for file storage
- Security groups and networking

### 2. Database Setup
```bash
cd backend
.\migrate-prod.bat
```

This:
- Runs Alembic migrations
- Creates database schema
- Sets up admin user (admin@hr-data-hub.com / AdminPass123!)

### 3. Backend Deployment

#### Option A: ECS Fargate (Recommended)
```bash
# Push to ECR
aws ecr create-repository --repository-name hr-data-hub
docker tag hr-data-hub:latest <account>.dkr.ecr.us-east-1.amazonaws.com/hr-data-hub:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/hr-data-hub:latest

# Create ECS service
aws ecs create-service --cli-input-json file://task-definition.json
```

#### Option B: EC2 Instance
```bash
# SSH to EC2 instance
ssh -i key.pem ec2-user@<instance-ip>

# Install Docker and run
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo docker run -d -p 8000:8000 --env-file .env.prod hr-data-hub:latest
```

### 4. Frontend Deployment
```bash
cd frontend
npm ci
VITE_API_URL=https://api.your-domain.com npm run build

# Deploy to S3 + CloudFront
aws s3 sync dist/ s3://your-frontend-bucket --delete
```

## Configuration

### Environment Variables
```bash
# Production environment (.env.prod)
DATABASE_URL=postgresql://postgres:PASSWORD@endpoint:5432/hr_data_hub
S3_BUCKET_NAME=prod-hr-data-hub-xml-files-123456789
SECRET_KEY=your-32-character-secret-key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com
```

### SSL/HTTPS Setup
```bash
# Request SSL certificate
aws acm request-certificate --domain-name your-domain.com

# Configure ALB with HTTPS listener
aws elbv2 create-listener --load-balancer-arn <alb-arn> \
  --protocol HTTPS --port 443 \
  --certificates CertificateArn=<cert-arn>
```

## Monitoring & Maintenance

### Health Checks
- API: `https://api.your-domain.com/health`
- Database: Monitor RDS CloudWatch metrics
- Storage: Monitor S3 usage and costs

### Logs
```bash
# View application logs
aws logs tail /ecs/hr-data-hub --follow

# View database logs
aws rds describe-db-log-files --db-instance-identifier hr-data-hub-prod
```

### Backup Strategy
- RDS automated backups (7 days retention)
- S3 versioning enabled for file storage
- Database snapshots before major updates

## Scaling

### Horizontal Scaling
```bash
# Scale ECS service
aws ecs update-service --service hr-data-hub --desired-count 3

# Auto Scaling Group for EC2
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name hr-data-hub-asg \
  --min-size 1 --max-size 5 --desired-capacity 2
```

### Database Scaling
```bash
# Scale RDS instance
aws rds modify-db-instance \
  --db-instance-identifier hr-data-hub-prod \
  --db-instance-class db.t3.medium \
  --apply-immediately
```

## Security Checklist

- ✅ HTTPS enabled with valid SSL certificate
- ✅ Database in private subnet
- ✅ Security groups restrict access
- ✅ Environment variables for secrets
- ✅ IAM roles with least privilege
- ✅ S3 bucket encryption enabled
- ✅ CloudTrail logging enabled

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx

# Test connection
telnet <db-endpoint> 5432
```

**File Upload Issues**
```bash
# Check S3 permissions
aws s3api get-bucket-policy --bucket <bucket-name>

# Test S3 access
aws s3 ls s3://<bucket-name>
```

**Authentication Issues**
```bash
# Check JWT configuration
curl -X POST https://api.your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hr-data-hub.com","password":"AdminPass123!"}'
```

## Cost Optimization

### Estimated Monthly Costs (us-east-1)
- RDS db.t3.micro: ~$15
- ECS Fargate (2 tasks): ~$30
- S3 storage (100GB): ~$3
- Data transfer: ~$10
- **Total: ~$58/month**

### Cost Reduction Tips
- Use Reserved Instances for predictable workloads
- Enable S3 lifecycle policies
- Monitor and optimize data transfer
- Use CloudWatch to track unused resources

## Support

For deployment issues:
1. Check CloudFormation stack events
2. Review application logs in CloudWatch
3. Verify security group configurations
4. Test database connectivity

**Emergency Rollback**
```bash
# Rollback CloudFormation stack
aws cloudformation cancel-update-stack --stack-name hr-data-hub-prod

# Restore database from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier hr-data-hub-rollback \
  --db-snapshot-identifier <snapshot-id>
```