import sqlite3
import functools

#### decorator to lof SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = args[0] if args else kwargs.get('query', '')
        print(f"Executing SQL Query: {query}")
        result = func(*args, **kwargs)
        print("Query executed successfully.")
        return result
    return wrapper



@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")