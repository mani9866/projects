import streamlit as st
import json
import pandas as pd
from auth_manager import AuthManager
from barcode_manager import BarcodeManager
from grocery_components import GroceryItem
from barcode_manager import BarcodeScanner
from database_manager import SQLiteDatabaseManager

# SQLite Database Configuration
DB_NAME = "grocery.db"


class SQLiteListManager:
    @staticmethod
    def list_exists(list_id):
        """Check if a list with the given ID exists in the database"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM grocery_lists WHERE list_id = ?', (list_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def get_all_lists():
        """Get all list IDs and their data from the database"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT list_id, items FROM grocery_lists')
        results = cursor.fetchall()
        conn.close()
        return results

    @staticmethod
    def save_list(list_id, items):
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        items_json = json.dumps([{
            'name': item.name,
            'category': item.category,
            'cost': item.cost,
            'mfg_date': item.mfg_date,
            'exp_date': item.exp_date,
            'barcode': getattr(item, 'barcode', None),
            'quantity': item.quantity  # Save quantity
        } for item in items])
        cursor.execute('''
            INSERT OR REPLACE INTO grocery_lists (list_id, items)
            VALUES (?, ?)
        ''', (list_id, items_json))
        conn.commit()
        conn.close()

    @staticmethod
    def load_list(list_id):
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT items FROM grocery_lists WHERE list_id = ?', (list_id,))
        result = cursor.fetchone()
        conn.close()
        if result and result[0]:
            items_data = json.loads(result[0])
            return [GroceryItem(
                item['name'],
                item['category'],
                item.get('cost'),
                item.get('mfg_date'),
                item.get('exp_date'),
                item.get('barcode'),
                item.get('quantity', 1)  # Load quantity, default to 1
            ) for item in items_data]
        return []

    @staticmethod
    def debug_list_contents():
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT list_id, items FROM grocery_lists')
        results = cursor.fetchall()
        conn.close()
        return results


def show_barcode_scanner():
    """Display the barcode scanner functionality"""
    st.header("📷 Barcode Scanner")
    if st.button("Scan Now"):
        scanned_barcode = BarcodeScanner.scan_barcode()
        if scanned_barcode:
            item_data = BarcodeManager.get_item_by_barcode(scanned_barcode)
            if item_data:
                st.success(f"Found item: {item_data['name']} ({item_data['category']})")
            else:
                st.error("No item found for the scanned barcode")

def show_user_management(username, role):
    """Display the user management section for admins"""
    st.header("👥 User Management")
    if role != 'admin':
        st.warning("Only administrators can manage users")
        return
    users = AuthManager.get_all_users()
    st.subheader("Existing Users")
    st.dataframe(pd.DataFrame(users, columns=["Username", "Role"]), hide_index=True)
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    new_role = st.selectbox("Role", ["user", "admin"])
    if st.button("Add User"):
        if AuthManager.create_user(new_username, new_password, new_role):
            st.success(f"User '{new_username}' added successfully")
            st.experimental_rerun()
        else:
            st.error(f"Failed to add user '{new_username}'")

