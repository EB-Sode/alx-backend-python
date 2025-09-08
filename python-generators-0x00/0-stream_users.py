import seed


def stream_users():
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM user_data;")
        rows = cursor.fetchall()
        for row in rows:
            yield row
        cursor.close()