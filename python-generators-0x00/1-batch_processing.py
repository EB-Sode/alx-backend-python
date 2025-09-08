def stream_users_in_batches(batch_size):
    """
    Generator function that yields user data in batches of a specified size.

    Args:
        batch_size (int): The number of user records to include in each batch.

    Yields:
        list: A list containing a batch of user records.
    """
    stream_users = __import__('0-stream_users')
    batch = []
    for user in stream_users.stream_users():
        batch.append(user)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch



def batch_processing(batch_size):
    """
    Processes user data in batches and prints each batch.

    Args:
        batch_size (int): The number of user records to include in each batch.
    """
    for batch in stream_users_in_batches(batch_size):
        print(batch)