# database.py
# All SQLite logic lives here. Nothing here knows about pygame/screens.

import sqlite3
import os
import hashlib
import binascii
from datetime import datetime
from config import DB_PATH
import paths


def get_connection():
    db_path = paths.writable_path(DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            played_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ---------- Password hashing (salted PBKDF2, stdlib only) ----------

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def _verify_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = binascii.unhexlify(salt_hex)
        expected = binascii.unhexlify(hash_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return dk == expected
    except Exception:
        return False


# ---------- Users ----------

def create_user(username, password):
    """Returns (True, user_id) on success, or (False, error_message)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"

    conn = get_connection()
    c = conn.cursor()
    try:
        password_hash = _hash_password(password)
        c.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        user_id = c.lastrowid
        return True, user_id
    except sqlite3.IntegrityError:
        return False, "That username is already taken"
    finally:
        conn.close()


def verify_login(username, password):
    """Returns user_id if valid, else None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username.strip(),))
    row = c.fetchone()
    conn.close()
    if row and _verify_password(password, row[1]):
        return row[0]
    return None


def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ---------- Games / scores ----------

def save_game(user_id, score, difficulty):
    conn = get_connection()
    c = conn.cursor()
    played_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # local time, not UTC
    c.execute(
        "INSERT INTO games (user_id, score, difficulty, played_at) VALUES (?, ?, ?, ?)",
        (user_id, score, difficulty, played_at),
    )
    conn.commit()
    conn.close()


def get_high_score(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM games WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else 0


def get_stats(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*), MAX(score), AVG(score) FROM games WHERE user_id = ?", (user_id,))
    games_played, best_score, avg_score = c.fetchone()

    stats = {
        "games_played": games_played or 0,
        "best_score": best_score or 0,
        "avg_score": round(avg_score, 2) if avg_score else 0,
    }

    for diff in ("Easy", "Medium", "Hard"):
        c.execute(
            "SELECT MAX(score) FROM games WHERE user_id = ? AND difficulty = ?",
            (user_id, diff),
        )
        row = c.fetchone()
        stats[f"best_{diff.lower()}"] = row[0] if row and row[0] is not None else 0

    conn.close()
    return stats


def get_leaderboard(difficulty=None, limit=10):
    """Returns list of (username, difficulty, best_score), best score per user, sorted desc."""
    conn = get_connection()
    c = conn.cursor()
    if difficulty:
        c.execute("""
            SELECT u.username, g.difficulty, MAX(g.score) as best
            FROM games g JOIN users u ON g.user_id = u.id
            WHERE g.difficulty = ?
            GROUP BY g.user_id
            ORDER BY best DESC
            LIMIT ?
        """, (difficulty, limit))
    else:
        c.execute("""
            SELECT u.username, g.difficulty, MAX(g.score) as best
            FROM games g JOIN users u ON g.user_id = u.id
            GROUP BY g.user_id
            ORDER BY best DESC
            LIMIT ?
        """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_history(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT played_at, difficulty, score
        FROM games
        WHERE user_id = ?
        ORDER BY played_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows