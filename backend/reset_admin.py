import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash

database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:secure_dev_password_123@localhost:5432/hr_data_hub')
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

admin_email = 'admin@hr-data-hub.com'
admin_password = 'AdminPass123!'

try:
    hashed_password = get_password_hash(admin_password)
    db.execute(text("UPDATE users SET hashed_password = :password WHERE email = :email"), 
               {"password": hashed_password, "email": admin_email})
    db.commit()
    print(f'Admin password reset for: {admin_email}')
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()