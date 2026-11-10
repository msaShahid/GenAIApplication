
import sqlite3

from config import DB_PATH, PRIORITIES, TASK_STATUSES


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK(status IN (
                        'Pending',
                        'In Progress',
                        'Completed'
                    )),
                priority TEXT NOT NULL DEFAULT 'Medium'
                    CHECK(priority IN (
                        'Low',
                        'Medium',
                        'High'
                    )),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_tasks_status
            ON tasks(status)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_tasks_priority
            ON tasks(priority)
        """)


def add_task(title, description="", priority="Medium"):

    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if len(title) > 200:
        raise ValueError("Task title is too long.")

    if priority not in PRIORITIES:
        raise ValueError("Invalid priority.")

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO tasks (title, description, priority)
            VALUES (?, ?, ?)
        """, (title, description.strip(), priority))

        return cursor.lastrowid


def get_tasks():

    with get_connection() as conn:

        return conn.execute("""
            SELECT *
            FROM tasks
            ORDER BY id DESC
        """).fetchall()


def update_task(task_id, status):

    if status not in TASK_STATUSES:
        raise ValueError("Invalid task status.")

    with get_connection() as conn:

        cursor = conn.execute("""
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        """, (status, task_id))

        return cursor.rowcount > 0


def delete_task(task_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM tasks
            WHERE id = ?
        """, (task_id,))

        return cursor.rowcount > 0


def get_task_statistics():

    with get_connection() as conn:

        return conn.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Pending'
                    THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'In Progress'
                    THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN status = 'Completed'
                    THEN 1 ELSE 0 END) AS completed
            FROM tasks
        """).fetchone()
