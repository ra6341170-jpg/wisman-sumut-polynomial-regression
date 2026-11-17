import hashlib
import os
import sqlite3

DB_NAME = "users.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


def hash_password(password, salt=None):
  if salt is None:
    salt = os.urandom(16).hex()
  hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
  return hashed, salt


def register_user(username, password):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  hashed, salt = hash_password(password)
  try:
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, hashed, salt),
    )
    conn.commit()
    conn.close()
    return True, "Registrasi berhasil! Silakan pindah ke tab Login."
  except sqlite3.IntegrityError:
    conn.close()
    return False, "Username sudah terdaftar. Silakan pilih username lain."


def verify_login(username, password):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
  )
  result = cursor.fetchone()
  conn.close()

  if result:
    stored_hash, salt = result
    check_hash, _ = hash_password(password, salt)
    if check_hash == stored_hash:
      return True, "Login berhasil!"
  return False, "Username atau password salah."