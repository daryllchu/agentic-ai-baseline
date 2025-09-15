import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:secure_dev_password_123@localhost:5432/hr_data_hub')
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

email = 'test@test.com'
password = 'test123'

try:
    # Delete existing user
    db.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
    
    # Get tenant ID
    tenant_result = db.execute(text("SELECT id FROM tenants WHERE domain = 'default' LIMIT 1")).fetchone()
    if not tenant_result:
        db.execute(text("INSERT INTO tenants (name, domain, is_active, created_at) VALUES ('Default', 'default', true, NOW())"))
        db.commit()
        tenant_result = db.execute(text("SELECT id FROM tenants WHERE domain = 'default' LIMIT 1")).fetchone()
    
    tenant_id = tenant_result[0]
    hashed_password = pwd_context.hash(password)
    
    # Create user
    db.execute(text("""
        INSERT INTO users (tenant_id, email, hashed_password, role, is_active, created_at) 
        VALUES (:tenant_id, :email, :password, 'admin', true, NOW())
    """), {"tenant_id": tenant_id, "email": email, "password": hashed_password})
    
    db.commit()
    print(f'Test user created: {email} / {password}')
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()