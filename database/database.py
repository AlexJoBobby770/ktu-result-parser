# database/database.py
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

# Absolute path so the .db file always saves next to this file
# regardless of where uvicorn is run from
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktu_results.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP NOT NULL,
            total_students INTEGER,
            total_departments INTEGER,
            status TEXT DEFAULT 'completed',
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def create_user(username: str, email: str, hashed_password: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute('''
            INSERT INTO users (username, email, hashed_password, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, datetime.now()))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()

    return dict(row) if row else None


def get_user_id(username: str) -> Optional[int]:
    user = get_user_by_username(username)
    return user['id'] if user else None


def save_session(session_id: str, filename: str, total_students: int,
                 total_departments: int, username: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    user_id = get_user_id(username) if username else None

    c.execute('''
        INSERT INTO sessions (session_id, filename, upload_time, total_students,
                            total_departments, status, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, filename, datetime.now(), total_students,
          total_departments, 'completed', user_id))

    conn.commit()
    conn.close()


def get_recent_sessions(limit: int = 10, username: str = None) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if username:
        user_id = get_user_id(username)
        c.execute('''
            SELECT session_id, filename, upload_time, total_students,
                   total_departments, status
            FROM sessions
            WHERE user_id = ?
            ORDER BY upload_time DESC
            LIMIT ?
        ''', (user_id, limit))
    else:
        c.execute('''
            SELECT session_id, filename, upload_time, total_students,
                   total_departments, status
            FROM sessions
            ORDER BY upload_time DESC
            LIMIT ?
        ''', (limit,))

    sessions = [dict(row) for row in c.fetchall()]
    conn.close()

    return sessions


def get_session(session_id: str, username: str = None) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if username:
        user_id = get_user_id(username)
        c.execute('''
            SELECT * FROM sessions
            WHERE session_id = ? AND user_id = ?
        ''', (session_id, user_id))
    else:
        c.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))

    row = c.fetchone()
    conn.close()

    return dict(row) if row else None


# Initialize DB when module is imported
init_db()