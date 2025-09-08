import mysql.connector
import pandas as pd

# ---------- Connect to MySQL (no database yet) ----------
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",         # 👈 adjust user
            password="sode007" # 👈 adjust password
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None


# ---------- Create Database ----------
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
    cursor.close()


# ---------- Connect to ALX_prodev ----------
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # 👈 adjust user
            password="sode007",   # 👈 adjust password
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None


# ---------- Create Table ----------
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        age DECIMAL(3,0) NOT NULL,
        INDEX (user_id)
    );
    """)
    cursor.close()

csv_url = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250908%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250908T205533Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=0b9787fd99aece75b7406b7afad4d5a570ea093fc3db3c34a525740f6eba9445"

# ---------- Insert Data from CSV ----------
def insert_data(connection, csv_url):
    df = pd.read_csv(csv_url)

    cursor = connection.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT IGNORE INTO user_data (user_id, name, email, age)
            VALUES (UUID(), %s, %s, %s)
        """, (row["name"], row["email"], row["age"]))

    connection.commit()
    cursor.close()
