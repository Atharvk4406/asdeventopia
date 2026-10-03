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
        ALTER TABLE events 
        ADD COLUMN registration_deadline DATETIME NULL DEFAULT NULL
    """)
    print("OK: Added registration_deadline column to events table.")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("INFO: Column already exists, skipping.")
    else:
        print("ERROR:", e)

conn.commit()
cursor.close()
conn.close()
print("Done.")
