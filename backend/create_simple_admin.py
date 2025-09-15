import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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
    # First create a default tenant if it doesn't exist
    tenant_result = db.execute(text("SELECT id FROM tenants WHERE domain = 'default' LIMIT 1")).fetchone()
    
    if not tenant_result:
        db.execute(text("""
            INSERT INTO tenants (name, domain, is_active, created_at) 
            VALUES ('Default Tenant', 'default', true, :created_at)
        """), {"created_at": datetime.now(timezone.utc)})
        db.commit()
        tenant_result = db.execute(text("SELECT id FROM tenants WHERE domain = 'default' LIMIT 1")).fetchone()
    
    tenant_id = tenant_result[0]
    
    # Check if admin user exists
    existing = db.execute(text("SELECT id FROM users WHERE email = :email LIMIT 1"), {"email": admin_email}).fetchone()
    
    if not existing:
        hashed_password = get_password_hash(admin_password)
        db.execute(text("""
            INSERT INTO users (tenant_id, email, hashed_password, role, is_active, created_at) 
            VALUES (:tenant_id, :email, :hashed_password, 'admin', true, :created_at)
        """), {
            "tenant_id": tenant_id,
            "email": admin_email,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc)
        })
        db.commit()
        print(f'Admin user created: {admin_email}')
    else:
        print('Admin user already exists')
        
except Exception as e:
    print(f'Error creating admin user: {e}')
finally:
    db.close()