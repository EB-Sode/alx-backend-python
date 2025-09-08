seed = __import__('seed')

connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print(f"connection successful")

    connection = seed.connect_to_prodev()

    csv_url = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250908%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250908T205533Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=0b9787fd99aece75b7406b7afad4d5a570ea093fc3db3c34a525740f6eba9445"

    if connection:
        seed.create_table(connection)
        seed.insert_data(connection, csv_url)
        cursor = connection.cursor()
        cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
        result = cursor.fetchone()
        if result:
            print(f"Database ALX_prodev is present ")
        cursor.execute(f"SELECT * FROM user_data LIMIT 10;")
        rows = cursor.fetchall()
        print(rows)
        cursor.close()


