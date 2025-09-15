# HR Data Exchange Hub

A cloud-based ETL platform for integrating employee data from multiple HR systems (starting with Workday) and providing standardized API responses.

## Architecture

- **Backend**: Python FastAPI with PostgreSQL
- **Frontend**: React with TypeScript (Sprint 4+)
- **Infrastructure**: AWS (EC2, RDS, S3, Lambda)
- **Queue**: Redis with Celery for background jobs

## Quick Start

### Local Development

1. **Start services with Docker Compose:**
```bash
cd backend
docker-compose up -d
```

2. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run database migrations:**
```bash
cd backend
alembic upgrade head
```

4. **Start the API server:**
```bash
cd backend
uvicorn main:app --reload
```

5. **Access the API:**
- API: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### AWS Infrastructure Deployment

1. **Deploy infrastructure:**
```bash
aws cloudformation create-stack \
  --stack-name hr-data-hub-dev \
  --template-body file://infrastructure/aws-infrastructure.yml \
  --parameters ParameterKey=Environment,ParameterValue=dev \
               ParameterKey=DBPassword,ParameterValue=YourSecurePassword123
```

2. **Update environment variables:**
```bash
export DATABASE_URL="postgresql://postgres:password@your-rds-endpoint:5432/hr_data_hub"
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Health Check
- `GET /health` - Service health status
- `GET /` - API information

## Testing

```bash
cd backend
pytest tests/
```

## Sprint 1 Deliverables ✅

- [x] AWS infrastructure setup (VPC, EC2, RDS, S3)
- [x] Database schema implementation
- [x] Development environment configuration
- [x] Basic project structure setup
- [x] JWT authentication system
- [x] Health check endpoints
- [x] Unit tests for authentication
- [x] Docker containerization
- [x] Database migrations with Alembic

## Next Steps (Sprint 2)

- ETL job framework with Celery
- XML file upload system
- Basic Workday XML processing
- Job monitoring and status tracking

## Environment Variables

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/hr_data_hub
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
```