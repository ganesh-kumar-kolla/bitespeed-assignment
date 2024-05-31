import sqlite3
from datetime import datetime

DATABASE = 'contacts.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phoneNumber TEXT,
                email TEXT,
                linkedId INTEGER,
                linkPrecedence TEXT CHECK(linkPrecedence IN ('primary', 'secondary')),
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                deletedAt DATETIME
            )
        ''')
        conn.commit()

init_db()