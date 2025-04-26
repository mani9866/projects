import sqlite3
import hashlib
import uuid

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

    @staticmethod
    def initialize_auth_database():
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        SQLiteDatabaseManager.create_default_users(cursor)
        conn.commit()
        conn.close()

    @staticmethod
    def create_default_users(cursor):
        """Create default admin and normal users if they don't exist"""
        # Check if admin user exists
        cursor.execute('SELECT 1 FROM users WHERE username = ?', ('root',))
        if not cursor.fetchone():
            # Create admin user
            salt = uuid.uuid4().hex
            password_hash = hashlib.sha256(('Admin@123' + salt).encode()).hexdigest()
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
                ('root', password_hash, salt, 'admin')
            )
        
        # Check if normal user exists
        cursor.execute('SELECT 1 FROM users WHERE username = ?', ('user01',))
        if not cursor.fetchone():
            # Create normal user
            salt = uuid.uuid4().hex
            password_hash = hashlib.sha256(('Test@123' + salt).encode()).hexdigest()
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
                ('user01', password_hash, salt, 'user')
            )

    @staticmethod
    def authenticate(username, password):
        """Authenticate a user and return their role if successful"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash, salt, role FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash, salt, role = result
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            if password_hash == stored_hash:
                return role
        
        return None

    @staticmethod
    def create_user(username, password, role='user'):
        """Create a new user"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Create new user
        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        cursor.execute(
            'INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
            (username, password_hash, salt, role)
        )
        
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all_users():
        """Get a list of all users and their roles"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, role FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return users

    @staticmethod
    def delete_user(username):
        """Delete a user"""
        # Don't allow deleting the root admin
        if username == 'root':
            return False
        
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
