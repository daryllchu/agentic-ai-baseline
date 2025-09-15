@echo off
REM Sprint 5 Production Deployment Script

echo 🚀 Deploying HR Data Exchange Hub - Sprint 5 Production Features...

REM Configuration
set STACK_NAME=hr-data-hub-prod-v5
set REGION=us-east-1

echo 📦 Building optimized Docker images...
cd backend
docker build -f Dockerfile.prod -t hr-data-hub:v5-prod .

echo 🔧 Running performance tests...
python -m pytest tests/test_performance.py -v

echo 📊 Deploying monitoring infrastructure...
aws cloudformation deploy ^
  --template-file infrastructure/monitoring-stack.yml ^
  --stack-name %STACK_NAME%-monitoring ^
  --capabilities CAPABILITY_IAM ^
  --region %REGION%

echo 🏗️ Deploying main application stack...
aws cloudformation deploy ^
  --template-file infrastructure/aws-infrastructure.yml ^
  --stack-name %STACK_NAME% ^
  --parameter-overrides Environment=prod Version=v5 ^
  --capabilities CAPABILITY_IAM ^
  --region %REGION%

echo 📈 Setting up monitoring dashboards...
aws logs create-log-group --log-group-name /aws/ecs/hr-data-hub-prod --region %REGION%

echo ✅ Sprint 5 Production Deployment Complete!
echo 📊 Features Deployed:
echo   • Multi-tenant architecture
echo   • Advanced monitoring & alerting
echo   • Performance optimization with caching
echo   • Comprehensive testing suite
echo   • Production-ready monitoring dashboard
echo.
echo 🔗 Access Points:
echo   • API: https://api.hr-data-hub.com
echo   • Monitoring: https://monitoring.hr-data-hub.com
echo   • Metrics: /api/monitoring/metrics
echo   • Health: /api/monitoring/health/detailed

pause