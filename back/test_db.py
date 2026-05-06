import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db.db_manager import get_connection

try:
    conn = get_connection()
    print("Database connection SUCCESS!")
    conn.close()
except Exception as e:
    print(f"Database connection FAILED: {e}")
