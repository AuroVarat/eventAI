import sqlite3
from pathlib import Path

# Database setup (runs once when the file is imported)
DB_PATH = Path("events.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT,
        location TEXT,
        user_id INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

def add_event(name, date, time=None, location=None, user_id=None):
    """Add a new event to the local database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (name, date, time, location, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, (name, date, time, location, user_id))
    conn.commit()
    conn.close()
    print(f"✅ Event '{name}' on {date} added successfully.")

def get_all_events():
    """Retrieve all events from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY date")
    events = cursor.fetchall()
    conn.close()
    return events
