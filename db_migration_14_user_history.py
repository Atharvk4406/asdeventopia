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
    CREATE TABLE IF NOT EXISTS user_activity_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        action_type VARCHAR(100) NOT NULL,
        action_details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Created 'user_activity_log' table successfully.")

    conn.commit()
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
