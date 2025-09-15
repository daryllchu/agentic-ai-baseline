@echo off
REM Production Database Migration Script

echo 🗄️ Running production database migrations...

REM Load environment variables
if exist .env.prod (
    for /f "tokens=1,2 delims==" %%a in (.env.prod) do set %%a=%%b
)

echo ⏳ Waiting for database connection...
python -c "import time; print('Waiting 10 seconds for database...'); time.sleep(10); print('Continuing with migration')"

echo 🔄 Running Alembic migrations...
alembic upgrade head

echo 👤 Creating admin user...
python create_admin.py

echo ✅ Database migration complete!
pause