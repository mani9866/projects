from database_manager import SQLiteDatabaseManager

class AuthManager:
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user and return their role if successful"""
        return SQLiteDatabaseManager.authenticate(username, password)

    @staticmethod
    def create_user(username, password, role='user'):
        """Create a new user"""
        return SQLiteDatabaseManager.create_user(username, password, role)

    @staticmethod
    def get_all_users():
        """Get a list of all users and their roles"""
        return SQLiteDatabaseManager.get_all_users()

    @staticmethod
    def delete_user(username):
        """Delete a user"""
        return SQLiteDatabaseManager.delete_user(username)

    @staticmethod
    def initialize_auth_database():
        """Initialize the authentication database"""
        SQLiteDatabaseManager.initialize_auth_database()