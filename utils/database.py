# =========================
# FILE: database.py
# =========================

import sqlite3
from pathlib import Path
import bcrypt

DB_NAME = Path(__file__).resolve().parent.parent / "users.db"


def get_connection():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        pregnancies REAL,
        glucose REAL,
        bmi REAL,
        age REAL,
        insulin REAL,

        prediction TEXT,
        probability REAL,

        created_at TEXT
    )
    """)

    # =========================
    # PROFILE TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        email TEXT,
        mobile TEXT,
        location TEXT,
        photo_path TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# AUTH
# =========================

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )


def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode()

    return bcrypt.checkpw(
        password.encode(),
        hashed
    )


def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (username, hashed)
        )

        cursor.execute("""
        INSERT INTO profiles(
            username,
            name,
            email,
            mobile,
            location,
            photo_path
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            username,
            "",
            "",
            "",
            ""
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        stored_password = user[2]

        if check_password(password, stored_password):
            return True

    return False


# =========================
# HISTORY
# =========================

def save_history(
    username,
    pregnancies,
    glucose,
    bmi,
    age,
    insulin,
    prediction,
    probability,
    created_at
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history(
        username,
        pregnancies,
        glucose,
        bmi,
        age,
        insulin,
        prediction,
        probability,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        pregnancies,
        glucose,
        bmi,
        age,
        insulin,
        prediction,
        probability,
        created_at
    ))

    conn.commit()
    conn.close()


def delete_all_history(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM history
    WHERE username=?
    """, (username,))

    conn.commit()
    conn.close()


def delete_history_by_id(history_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM history
    WHERE id=?
    """, (int(history_id),))

    conn.commit()
    conn.close()


# =========================
# PROFILE
# =========================

def get_profile(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, name, email, mobile, location, photo_path
    FROM profiles
    WHERE username=?
    """, (username,))

    profile = cursor.fetchone()

    if profile is None:
        cursor.execute("""
        INSERT INTO profiles(
            username,
            name,
            email,
            mobile,
            location,
            photo_path
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            username,
            "",
            "",
            "",
            ""
        ))

        conn.commit()

        cursor.execute("""
        SELECT username, name, email, mobile, location, photo_path
        FROM profiles
        WHERE username=?
        """, (username,))

        profile = cursor.fetchone()

    conn.close()

    return profile


def update_profile(
    username,
    name,
    email,
    mobile,
    location,
    photo_path
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO profiles(
        username,
        name,
        email,
        mobile,
        location,
        photo_path
    )
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(username) DO UPDATE SET
        name=excluded.name,
        email=excluded.email,
        mobile=excluded.mobile,
        location=excluded.location,
        photo_path=excluded.photo_path
    """, (
        username,
        name,
        email,
        mobile,
        location,
        photo_path
    ))

    conn.commit()
    conn.close()