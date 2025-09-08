def stream_user_ages():
    """
    Generator that yields ages of users from the user_data table.
    """
    import seed

    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data;")
        for (age,) in cursor:
            yield age
        cursor.close()
        connection.close()

def average_age():
    """
    Calculates the average age of users in the user_data table.
    """
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
        average_age = total_age / count if count > 0 else 0
    return f"Average age of users: {average_age}"