import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        # Open connection
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        # Execute query with parameters
        self.cursor.execute(self.query, self.params)
        # Fetch results immediately (before closing connection)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        # Don’t suppress exceptions
        return False

query = "SELECT * FROM users WHERE age > ?"
param = (25,)

with ExecuteQuery("users.db", query, param) as results:
    print("Users older than 25:")
    for row in results:
        print(row)
