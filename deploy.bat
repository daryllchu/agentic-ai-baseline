@echo off
REM HR Data Exchange Hub Windows Deployment Script

echo 🚀 Deploying HR Data Exchange Hub...

REM Configuration
set STACK_NAME=hr-data-hub-prod
set REGION=us-east-1

REM Generate secure passwords
for /f %%i in ('powershell -Command "[System.Web.Security.Membership]::GeneratePassword(32, 8)"') do set DB_PASSWORD=%%i
for /f %%i in ('powershell -Command "[System.Web.Security.Membership]::GeneratePassword(32, 8)"') do set SECRET_KEY=%%i

echo 📦 Deploying AWS infrastructure...
aws cloudformation deploy ^
  --template-file infrastructure/aws-infrastructure.yml ^
  --stack-name %STACK_NAME% ^
  --parameter-overrides Environment=prod DBPassword=%DB_PASSWORD% ^
  --capabilities CAPABILITY_IAM ^
  --region %REGION%

echo 📋 Getting infrastructure details...
for /f %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue" --output text --region %REGION%') do set DB_ENDPOINT=%%i
for /f %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue" --output text --region %REGION%') do set S3_BUCKET=%%i

echo ⚙️ Creating production configuration...
(
echo DATABASE_URL=postgresql://postgres:%DB_PASSWORD%@%DB_ENDPOINT%:5432/hr_data_hub
echo S3_BUCKET_NAME=%S3_BUCKET%
echo SECRET_KEY=%SECRET_KEY%
echo ENVIRONMENT=production
echo DEBUG=false
echo LOG_LEVEL=INFO
echo ALLOWED_ORIGINS=https://your-domain.com
) > backend\.env.prod

echo 🐳 Building Docker image...
cd backend
docker build -f Dockerfile.prod -t hr-data-hub:latest .

echo ✅ Deployment configuration complete!
echo 📊 Infrastructure Details:
echo   Database: %DB_ENDPOINT%
echo   S3 Bucket: %S3_BUCKET%
echo.
echo 🔐 Credentials saved to backend\.env.prod
echo ⚠️  Store DB_PASSWORD securely: %DB_PASSWORD%
echo.
echo 🚀 Next steps:
echo   1. Run: cd backend ^&^& migrate-prod.bat
echo   2. Push image to ECR
echo   3. Configure domain and SSL

pause