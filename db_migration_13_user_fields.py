import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Atharv",
        database="eventhopia"
    )
    cursor = conn.cursor()

    cursor.execute("""
    ALTER TABLE users
    ADD COLUMN email VARCHAR(100),
    ADD COLUMN class VARCHAR(50);
    """)
    print("Added email and class columns to 'users' table successfully.")

    conn.commit()
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
