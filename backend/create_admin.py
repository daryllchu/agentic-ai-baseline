import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from auth import get_password_hash
from datetime import datetime, timezone

# Use environment variable or default
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:secure_dev_password_123@localhost:5432/hr_data_hub')

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

admin_email = 'admin@hr-data-hub.com'
admin_password = 'AdminPass123!'

try:
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
except Exception as e:
    print(f'Error creating admin user: {e}')
finally:
    db.close()