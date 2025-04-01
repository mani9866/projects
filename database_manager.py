import sqlite3

DB_NAME = "grocery.db"

class SQLiteDatabaseManager:
    @staticmethod
    def create_connection():
        return sqlite3.connect(DB_NAME)

    @staticmethod
    def initialize_database():
        """Initialize the database with required tables"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grocery_lists (
                list_id TEXT PRIMARY KEY,
                items TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barcodes (
                barcode TEXT PRIMARY KEY,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                default_cost REAL
            )
        ''')
        conn.commit()
        conn.close()
