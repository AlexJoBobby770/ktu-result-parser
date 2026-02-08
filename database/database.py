# backend/database.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "ktu_results.db"

def init_db():
    """Initialize database with sessions table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP NOT NULL,
            total_students INTEGER,
            total_departments INTEGER,
            status TEXT DEFAULT 'completed'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def save_session(session_id: str, filename: str, total_students: int, total_departments: int):
    """Save a new upload session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO sessions (session_id, filename, upload_time, total_students, total_departments, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, filename, datetime.now(), total_students, total_departments, 'completed'))
    
    conn.commit()
    conn.close()


def get_recent_sessions(limit: int = 10) -> List[Dict]:
    """Get most recent upload sessions"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    c = conn.cursor()
    
    c.execute('''
        SELECT session_id, filename, upload_time, total_students, total_departments, status
        FROM sessions
        ORDER BY upload_time DESC
        LIMIT ?
    ''', (limit,))
    
    sessions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return sessions


def get_session(session_id: str) -> Optional[Dict]:
    """Get a specific session by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None


# Initialize DB when module is imported
init_db()