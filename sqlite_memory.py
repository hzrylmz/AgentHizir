import sqlite3
from datetime import datetime

class SQLiteMemory:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')
        self.conn.commit()

    def add_message(self, role, content):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversation (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        )
        self.conn.commit()

    def get_conversation(self, last_n=None):
        cursor = self.conn.cursor()
        if last_n:
            query = """
                SELECT id, role, content, timestamp FROM conversation
                ORDER BY id DESC LIMIT ?
            """
            cursor.execute(query, (last_n,))
            results = cursor.fetchall()
            results = list(results)[::-1]  
        else:
            query = "SELECT id, role, content, timestamp FROM conversation ORDER BY id ASC"
            cursor.execute(query)
            results = cursor.fetchall()
        return results

    def delete_message(self, msg_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversation WHERE id = ?", (msg_id,))
        self.conn.commit()

    def clear(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversation")
        self.conn.commit()

    def close(self):
        self.conn.close()
