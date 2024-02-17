import os
import sqlite3
from pathlib import Path
from rsa import PublicKey, PrivateKey, encrypt, decrypt

def load_public_key():
    """
    Load the public key from the database.
    """
    home_dir = str(Path.home())
    db_path = os.path.join(home_dir, ".keychain", "keys.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT keypart FROM keys WHERE id = 1")
    n = int(cursor.fetchone()[0])

    cursor.execute("SELECT keypart FROM keys WHERE id = 2")
    e = int(cursor.fetchone()[0])

    conn.close()

    public_key = PublicKey(n, e)
    return public_key

def load_private_key():
    """
    Load the private key from the database.
    """
    home_dir = str(Path.home())
    db_path = os.path.join(home_dir, ".keychain", "keys.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT keypart FROM keys WHERE id = 1")
    n = int(cursor.fetchone()[0])

    cursor.execute("SELECT keypart FROM keys WHERE id = 2")
    e = int(cursor.fetchone()[0])

    cursor.execute("SELECT keypart FROM keys WHERE id = 3")
    d = int(cursor.fetchone()[0])

    cursor.execute("SELECT keypart FROM keys WHERE id = 4")
    p = int(cursor.fetchone()[0])

    cursor.execute("SELECT keypart FROM keys WHERE id = 5")
    q = int(cursor.fetchone()[0])

    conn.close()

    private_key = PrivateKey(n, e, d, p, q)
    return private_key

def encrypt_message(message):
    """
    Encrypt a message using the public key.
    """
    public_key = load_public_key()
    encrypted_message = encrypt(message.encode('utf-8'), public_key)
    return encrypted_message

def decrypt_message(encrypted_message):
    """
    Decrypt a message using the private key.
    """
    private_key = load_private_key()
    decrypted_message = decrypt(encrypted_message, private_key)
    return decrypted_message.decode('utf-8')
