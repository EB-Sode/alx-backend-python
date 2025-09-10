import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        # Open database connection
        self.conn = sqlite3.connect(self.db_name)
        print(f"Connected to database: {self.db_name}")
        return self.conn   # This is what gets assigned to `as` in the with-block

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If an exception happened, rollback
        if exc_type:
            self.conn.rollback()
            print(f"Transaction rolled back due to: {exc_val}")
        else:
            self.conn.commit()
            print("Transaction committed successfully.")
        
        # Always close connection
        self.conn.close()
        print("Connection closed.")

        # Returning False lets exceptions propagate after cleanup
        return False

with DatabaseConnection("users.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())
