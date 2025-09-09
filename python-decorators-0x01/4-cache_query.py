import time
import sqlite3 
import functools

def with_db_connection(func):
    """opens a database connection, passes it to the function and closes it afterwards""" 
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

query_cache = {}

"""caches query results based on the SQL query string"""
def cache_query(func):
    @functools.wrap(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("Cache hit:", query)
            return query_cache[query]

        print("Cache miss:", query)
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result

    return wrapper



@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")