# keychain_operations.py

import os
import sqlite3
import shutil
from pathlib import Path
from rsa import newkeys

def create_database(db_path):
    """
    Create a SQLite database with the necessary table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
                        id INTEGER PRIMARY KEY,
                        keypart TEXT
                      )''')

    conn.commit()
    conn.close()

def create_keychain(re_create, keychain_dir):
    """
    Create a keychain directory and keys database if they don't exist.
    """
    if re_create and os.path.exists(keychain_dir):
        shutil.rmtree(keychain_dir)

    os.makedirs(keychain_dir)

    db_path = os.path.join(keychain_dir, "keys.db")
    create_database(db_path)

def generate_keys(key_size, re_create, keychain_dir):
    """
    Generate RSA keys and store them in the database.
    """
    create_keychain(re_create, keychain_dir)
    db_path = os.path.join(keychain_dir, "keys.db")

    public_key, private_key = newkeys(key_size)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert keys into the database
    cursor.execute("INSERT INTO keys (id, keypart) VALUES (?, ?)", (1, str(public_key.n)))
    cursor.execute("INSERT INTO keys (id, keypart) VALUES (?, ?)", (2, str(public_key.e)))
    cursor.execute("INSERT INTO keys (id, keypart) VALUES (?, ?)", (3, str(private_key.d)))
    cursor.execute("INSERT INTO keys (id, keypart) VALUES (?, ?)", (4, str(private_key.p)))
    cursor.execute("INSERT INTO keys (id, keypart) VALUES (?, ?)", (5, str(private_key.q)))

    conn.commit()
    conn.close()

    return "Keys generated and stored successfully."
