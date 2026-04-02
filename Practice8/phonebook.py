import csv
from connect import get_connection


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL UNIQUE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table created successfully.")


def insert_from_console():
    username = input("Enter username: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (username, phone) VALUES (%s, %s)",
        (username, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added.")


def insert_from_csv(filename="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (username, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING",
                (row["username"], row["phone"])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV data inserted.")


def query_all():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook ORDER BY id")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def query_by_name():
    name = input("Enter name to search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE username ILIKE %s",
        (f"%{name}%",)
    )

    rows = cur.fetchall()
    for row in rows:
        print(row)

    cur.close()
    conn.close()


def query_by_phone_prefix():
    prefix = input("Enter phone prefix: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE phone LIKE %s",
        (f"{prefix}%",)
    )

    rows = cur.fetchall()
    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    old_username = input("Enter existing username: ")
    new_username = input("Enter new username (or press Enter to skip): ")
    new_phone = input("Enter new phone (or press Enter to skip): ")

    conn = get_connection()
    cur = conn.cursor()

    if new_username and new_phone:
        cur.execute(
            "UPDATE phonebook SET username=%s, phone=%s WHERE username=%s",
            (new_username, new_phone, old_username)
        )
    elif new_username:
        cur.execute(
            "UPDATE phonebook SET username=%s WHERE username=%s",
            (new_username, old_username)
        )
    elif new_phone:
        cur.execute(
            "UPDATE phonebook SET phone=%s WHERE username=%s",
            (new_phone, old_username)
        )
    else:
        print("Nothing to update.")
        cur.close()
        conn.close()
        return

    conn.commit()
    cur.close()
    conn.close()
    print("Contact updated.")


def delete_contact():
    choice = input("Delete by (1) username or (2) phone? ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        username = input("Enter username: ")
        cur.execute("DELETE FROM phonebook WHERE username=%s", (username,))
    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
    else:
        print("Invalid choice.")
        cur.close()
        conn.close()
        return

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted.")

    
def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create table")
        print("2. Insert from CSV")
        print("3. Insert from console")
        print("4. Show all contacts")
        print("5. Search by name")
        print("6. Search by phone prefix")
        print("7. Update contact")
        print("8. Delete contact")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            insert_from_console()
        elif choice == "4":
            query_all()
        elif choice == "5":
            query_by_name()
        elif choice == "6":
            query_by_phone_prefix()
        elif choice == "7":
            update_contact()
        elif choice == "8":
            delete_contact()
        elif choice == "0":
            print("See you later Admin Yernar")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()