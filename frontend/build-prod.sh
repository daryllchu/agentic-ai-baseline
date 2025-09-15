#!/bin/bash

# Frontend Production Build Script
set -e

echo "🏗️ Building frontend for production..."

# Install dependencies
npm ci

# Build for production
VITE_API_URL=https://api.your-domain.com npm run build

# Create S3 deployment script
cat > deploy-frontend.sh << 'EOF'
#!/bin/bash
BUCKET_NAME="your-frontend-bucket"
aws s3 sync dist/ s3://$BUCKET_NAME --delete
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
EOF

chmod +x deploy-frontend.sh

echo "✅ Frontend build complete!"
echo "📁 Build files in: dist/"
echo "🚀 Run ./deploy-frontend.sh to deploy to S3"