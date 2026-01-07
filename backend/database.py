"""
Study Pilot AI - SQLite Database Models
Offline-first storage for users, courses, progress, and quiz history
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "data" / "study_pilot.db"


def get_connection():
    """Get database connection with row factory."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            syllabus_json TEXT,
            topics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Topics table (knowledge components)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            week_number INTEGER,
            difficulty REAL DEFAULT 0.5,
            prerequisites_json TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    # User progress (mastery tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            mastery_level REAL DEFAULT 0.0,
            p_learn REAL DEFAULT 0.3,
            p_guess REAL DEFAULT 0.25,
            p_slip REAL DEFAULT 0.1,
            attempts INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (topic_id) REFERENCES topics(id),
            UNIQUE(user_id, topic_id)
        )
    """)

    # Quiz history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            questions_json TEXT NOT NULL,
            responses_json TEXT,
            score REAL,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    # Study plans (roadmaps)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            plan_json TEXT NOT NULL,
            goal_date DATE,
            hours_per_week REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    # Documents (for RAG)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            filename TEXT NOT NULL,
            doc_type TEXT,
            content_chunks_json TEXT,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    conn.commit()
    conn.close()


# ============ User Functions ============

def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = "study_pilot_salt_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def create_user(name: str, email: str, password: str) -> dict:
    """Create a new user and return with API key."""
    conn = get_connection()
    cursor = conn.cursor()
    
    api_key = generate_api_key()
    password_hash = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, api_key) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, api_key)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "name": name, "email": email, "api_key": api_key}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user and return user data with API key."""
    conn = get_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute(
        "SELECT id, name, email, api_key FROM users WHERE email = ? AND password_hash = ?",
        (email, password_hash)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_api_key(api_key: str) -> dict:
    """Get user by API key for authentication."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, email FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


# ============ Course Functions ============

def create_course(name: str, code: str, description: str, syllabus: dict, topics: list) -> int:
    """Create a new course."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO courses (name, code, description, syllabus_json, topics_json) VALUES (?, ?, ?, ?, ?)",
        (name, code, description, json.dumps(syllabus), json.dumps(topics))
    )
    conn.commit()
    course_id = cursor.lastrowid
    
    # Create topics
    for i, topic in enumerate(topics):
        cursor.execute(
            "INSERT INTO topics (course_id, name, description, week_number, difficulty, prerequisites_json) VALUES (?, ?, ?, ?, ?, ?)",
            (course_id, topic['name'], topic.get('description', ''), 
             topic.get('week', i+1), topic.get('difficulty', 0.5),
             json.dumps(topic.get('prerequisites', [])))
        )
    
    conn.commit()
    conn.close()
    return course_id


def get_all_courses() -> list:
    """Get all available courses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, code, description FROM courses")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_course(course_id: int) -> dict:
    """Get course by ID with topics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    
    if not course:
        conn.close()
        return None
    
    cursor.execute("SELECT * FROM topics WHERE course_id = ? ORDER BY week_number", (course_id,))
    topics = cursor.fetchall()
    conn.close()
    
    result = dict(course)
    result['topics'] = [dict(t) for t in topics]
    return result


# ============ Progress Functions ============

def get_or_create_progress(user_id: int, topic_id: int) -> dict:
    """Get or create progress record for user-topic pair."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM progress WHERE user_id = ? AND topic_id = ?",
        (user_id, topic_id)
    )
    row = cursor.fetchone()
    
    if not row:
        cursor.execute(
            "INSERT INTO progress (user_id, topic_id) VALUES (?, ?)",
            (user_id, topic_id)
        )
        conn.commit()
        cursor.execute(
            "SELECT * FROM progress WHERE user_id = ? AND topic_id = ?",
            (user_id, topic_id)
        )
        row = cursor.fetchone()
    
    conn.close()
    return dict(row)


def update_progress(user_id: int, topic_id: int, mastery_level: float, 
                    correct: bool, p_learn: float = None) -> dict:
    """Update progress after quiz attempt."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current progress
    progress = get_or_create_progress(user_id, topic_id)
    
    new_attempts = progress['attempts'] + 1
    new_correct = progress['correct_count'] + (1 if correct else 0)
    
    update_fields = [
        "mastery_level = ?",
        "attempts = ?",
        "correct_count = ?",
        "last_updated = ?"
    ]
    params = [mastery_level, new_attempts, new_correct, datetime.now()]
    
    if p_learn is not None:
        update_fields.append("p_learn = ?")
        params.append(p_learn)
    
    params.extend([user_id, topic_id])
    
    cursor.execute(
        f"UPDATE progress SET {', '.join(update_fields)} WHERE user_id = ? AND topic_id = ?",
        params
    )
    conn.commit()
    conn.close()
    
    return get_or_create_progress(user_id, topic_id)


def get_user_progress(user_id: int, course_id: int = None) -> list:
    """Get all progress records for a user, optionally filtered by course."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if course_id:
        cursor.execute("""
            SELECT p.*, t.name as topic_name, t.course_id, c.name as course_name
            FROM progress p
            JOIN topics t ON p.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE p.user_id = ? AND t.course_id = ?
            ORDER BY t.week_number
        """, (user_id, course_id))
    else:
        cursor.execute("""
            SELECT p.*, t.name as topic_name, t.course_id, c.name as course_name
            FROM progress p
            JOIN topics t ON p.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE p.user_id = ?
            ORDER BY c.name, t.week_number
        """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ Quiz History Functions ============

def save_quiz(user_id: int, course_id: int, questions: list) -> int:
    """Save a new quiz."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO quiz_history (user_id, course_id, questions_json) VALUES (?, ?, ?)",
        (user_id, course_id, json.dumps(questions))
    )
    conn.commit()
    quiz_id = cursor.lastrowid
    conn.close()
    
    return quiz_id


def submit_quiz(quiz_id: int, responses: list, score: float) -> dict:
    """Submit quiz responses and score."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE quiz_history SET responses_json = ?, score = ?, completed_at = ? WHERE id = ?",
        (json.dumps(responses), score, datetime.now(), quiz_id)
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM quiz_history WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_quiz_history(user_id: int, course_id: int = None) -> list:
    """Get quiz history for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if course_id:
        cursor.execute(
            "SELECT * FROM quiz_history WHERE user_id = ? AND course_id = ? ORDER BY created_at DESC",
            (user_id, course_id)
        )
    else:
        cursor.execute(
            "SELECT * FROM quiz_history WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ Study Plan Functions ============

def save_study_plan(user_id: int, course_id: int, plan: dict, 
                    goal_date: str = None, hours_per_week: float = None) -> int:
    """Save a study plan."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO study_plans (user_id, course_id, plan_json, goal_date, hours_per_week) VALUES (?, ?, ?, ?, ?)",
        (user_id, course_id, json.dumps(plan), goal_date, hours_per_week)
    )
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    
    return plan_id


def get_latest_study_plan(user_id: int, course_id: int) -> dict:
    """Get the most recent study plan for a user-course pair."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM study_plans WHERE user_id = ? AND course_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id, course_id)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['plan'] = json.loads(result['plan_json'])
        return result
    return None


# Initialize database on import
init_database()
