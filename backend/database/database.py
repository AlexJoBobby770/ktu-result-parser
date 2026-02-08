# database/database.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "ktu_results.db"

def init_db():
    """Initialize database with sessions and users tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Sessions table (existing)
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
    
    # Users table (new)
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


# User functions
def create_user(username: str, email: str, hashed_password: str) -> bool:
    """Create a new user"""
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
        return False  # Username already exists


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_user_id(username: str) -> Optional[int]:
    """Get user ID by username"""
    user = get_user_by_username(username)
    return user['id'] if user else None


# Session functions (updated)
def save_session(session_id: str, filename: str, total_students: int, 
                 total_departments: int, username: str = None):
    """Save a new upload session"""
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
    """Get most recent upload sessions (optionally filtered by user)"""
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
    """Get a specific session by ID (optionally check user ownership)"""
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