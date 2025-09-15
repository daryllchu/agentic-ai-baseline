#!/usr/bin/env python3
"""Simple database management tool"""

import sys
from sqlalchemy import text
from database import get_db, engine
from models import *

def execute_query(query):
    """Execute raw SQL query"""
    db = next(get_db())
    try:
        result = db.execute(text(query))
        if query.strip().upper().startswith('SELECT'):
            rows = result.fetchall()
            for row in rows:
                print(row)
        else:
            db.commit()
            print(f"Query executed. Rows affected: {result.rowcount}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

def show_tables():
    """Show all tables"""
    execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

def show_employees():
    """Show all employees"""
    execute_query("SELECT id, employee_id, first_name, last_name, email, department FROM employees LIMIT 10")

def show_changes():
    """Show recent changes"""
    execute_query("""
        SELECT c.id, e.first_name, e.last_name, c.field_name, c.old_value, c.new_value, c.change_type, c.created_at 
        FROM employee_change_logs c 
        JOIN employees e ON c.employee_id = e.id 
        ORDER BY c.created_at DESC LIMIT 10
    """)

def clear_data():
    """Clear all data"""
    execute_query("DELETE FROM employee_change_logs")
    execute_query("DELETE FROM employees")
    execute_query("DELETE FROM etl_jobs")
    print("All data cleared")

def main():
    if len(sys.argv) < 2:
        print("Usage: python db_tool.py <command>")
        print("Commands:")
        print("  tables - Show all tables")
        print("  employees - Show employees")
        print("  changes - Show recent changes")
        print("  clear - Clear all data")
        print("  sql '<query>' - Execute raw SQL")
        return
    
    command = sys.argv[1]
    
    if command == "tables":
        show_tables()
    elif command == "employees":
        show_employees()
    elif command == "changes":
        show_changes()
    elif command == "clear":
        clear_data()
    elif command == "sql" and len(sys.argv) > 2:
        execute_query(sys.argv[2])
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()