import sys
import sqlite3
import os


def createtables(conn, extra_tables=None):
    """Create all required tables if they don't exist.
    extra_tables: list of table names to create dynamically (optional).
    """
    cursor = conn.cursor()

    # Core tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            name TEXT,
            job TEXT,
            department TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT
            )
        """)
    
    # Extra dynamic tables (like trainings)
    if extra_tables:
        for table_name in extra_tables:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    employee_name TEXT,
                    department TEXT,
                    status TEXT DEFAULT 'Pending'
                )
            """)

    conn.commit()


def run_query(conn, query, params=None, fetchone=False, commit=False, return_id=False):
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if commit:
        conn.commit()
        if return_id:
            return cursor.lastrowid
        return cursor.rowcount  # optional: number of rows changed

    if fetchone:
        return cursor.fetchone()
    return cursor.fetchall()