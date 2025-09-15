#!/bin/bash

# Production Database Migration Script
set -e

echo "🗄️ Running production database migrations..."

# Load environment variables
if [ -f .env.prod ]; then
    export $(cat .env.prod | xargs)
fi

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import psycopg2
import time
import os
from urllib.parse import urlparse

url = urlparse(os.getenv('DATABASE_URL'))
for i in range(30):
    try:
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]
        )
        conn.close()
        print('Database ready!')
        break
    except:
        print(f'Attempt {i+1}/30: Database not ready, waiting...')
        time.sleep(10)
else:
    raise Exception('Database connection timeout')
"

# Run migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

# Create initial admin user (optional)
echo "👤 Creating admin user..."
python -c "
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from auth import get_password_hash
from datetime import datetime, timezone

engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

admin_email = 'admin@hr-data-hub.com'
admin_password = 'AdminPass123!'

existing = db.query(User).filter(User.email == admin_email).first()
if not existing:
    admin_user = User(
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        created_at=datetime.now(timezone.utc)
    )
    db.add(admin_user)
    db.commit()
    print(f'Admin user created: {admin_email}')
else:
    print('Admin user already exists')

db.close()
"

echo "✅ Database migration complete!"