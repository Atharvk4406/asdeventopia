import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Atharv",
    "database": "eventhopia"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN phone VARCHAR(15) NULL DEFAULT NULL
    """)
    print("OK: Added phone column to users table.")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("SKIP: phone column already exists.")
    else:
        print(f"ERROR: {e}")

conn.commit()
cursor.close()
conn.close()
