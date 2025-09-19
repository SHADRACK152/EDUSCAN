import sqlite3
import os
import pickle

DB_PATH = "database/students.db"

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT,
        face_encoding BLOB,
        voice_path TEXT
    )
    """)

    # Attendance Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        name TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

from datetime import datetime

def log_attendance(student_id, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)", 
              (student_id, name, now))
    conn.commit()
    conn.close()

def save_student(student_id, name, encoding, voice_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO students (student_id, name, face_encoding, voice_path) VALUES (?, ?, ?, ?)",
                  (student_id, name, pickle.dumps(encoding), voice_path))
        conn.commit()
        print(f"[INFO] Student {name} saved.")
    except sqlite3.IntegrityError:
        print("[ERROR] Student ID already exists.")
    conn.close()

def load_all_encodings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT student_id, name, face_encoding FROM students")
    rows = c.fetchall()

    ids = []
    names = []
    encodings = []

    for sid, name, blob in rows:
        ids.append(sid)
        names.append(name)
        encodings.append(pickle.loads(blob))

    conn.close()
    return ids, names, encodings
