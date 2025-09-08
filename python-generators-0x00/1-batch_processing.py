import seed

def stream_users_in_batches(batch_size):
    """
    Generator that yields user data in batches directly from DB.
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield rows
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    """
    Processes user data in batches and prints each batch.
    """

    results = []
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user.age > 25:
                results.append(user)
    return results