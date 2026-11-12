from database import create_tables, get_connection


def insert_dummy_records():
    create_tables()
    connection = get_connection()

    pensioners = [
        ("Tandrima Nandy", "PPO202400123", "1958-05-15",
         "State Bank of India", "123456789012", "SBIN0001234",
         "tandrimanandy2002@gmail.com", "7439067577"),
        ("Rudra Das", "PPO202400456", "1960-08-20",
         "Punjab National Bank", "456789123012", "PUNB0001234",
         "mr.babaidas2004@gmail.com", "9000000002"),
        ("Sumonta Kolley", "PPO202404456", "1960-08-20",
         "Punjab National Bank", "459789123012", "PUNB0001234",
         "sumontakolley7@gmail.com", "7439504117")
    ]

    connection.executemany("""
        INSERT OR IGNORE INTO pensioners (
            name, ppo_number, date_of_birth,
            bank_name, account_number, ifsc, email, mobile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, pensioners)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    insert_dummy_records()
    print("Dummy pensioner records inserted successfully.")