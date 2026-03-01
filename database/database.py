# database/database.py
import sqlite3
import os
from datetime import datetime
from typing import Dict, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktu_results.db")

def init_db():
    """Initialize database with users table only"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def create_user(username: str, email: str, hashed_password: str) -> bool:
    """Create new user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO users (username, email, hashed_password, created_at) VALUES (?, ?, ?, ?)',
            (username, email, hashed_password, datetime.now())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


init_db()