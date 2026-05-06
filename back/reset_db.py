import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
import pymysql

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_NAME = os.getenv("DB_NAME", "chatbotdb")

def reset_database():
    print(f"Connecting to MySQL/MariaDB at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    print(f"Dropping database {DB_NAME} if exists...")
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    print(f"Creating database {DB_NAME}...")
    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    conn.close()
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
    from db.db_manager import init_db
    print("Running init_db()...")
    init_db()
    print("init_db() complete. Local database is now perfectly up to date with 001_init_tables.sql.")
