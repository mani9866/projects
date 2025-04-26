import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import speech_recognition as sr
from io import BytesIO
from abc import ABC, abstractmethod
import re
import datetime as dt
import hashlib
import uuid
import time
import cv2
import os
from auth_manager import AuthManager
from helpers import VoiceInputHandler, PDFReport
from barcode_manager import BarcodeManager
from grocery_components import GroceryComponent, GroceryItem, GroceryCategory
from barcode_scanner import BarcodeScanner
from database_manager import SQLiteDatabaseManager

# SQLite Database Configuration
DB_NAME = "grocery.db"

# Database Manager Class
class SQLiteDatabaseManager:
    @staticmethod
    def create_connection():
        return sqlite3.connect(DB_NAME)

    @staticmethod
    def initialize_database():
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grocery_lists (
                list_id TEXT PRIMARY KEY,
                items TEXT
            )
        ''')  # Correctly terminated string literal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barcodes (
                barcode TEXT PRIMARY KEY,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                default_cost REAL
            )
        ''')  # Correctly terminated string literal
        conn.commit()
        conn.close()
        AuthManager.initialize_auth_database()

# Composite Pattern Implementation
class GroceryComponent(ABC):
    @abstractmethod
    def display(self):
        pass

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

# Barcode Management
class BarcodeManager:
    @staticmethod
    def save_barcode(barcode, item_name, category, default_cost=None):
        """Save or update a barcode entry"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO barcodes (barcode, item_name, category, default_cost)
            VALUES (?, ?, ?, ?)
        ''', (barcode, item_name, category, default_cost))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_item_by_barcode(barcode):
        """Look up an item by its barcode"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT item_name, category, default_cost FROM barcodes WHERE barcode = ?', (barcode,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'name': result[0],
                'category': result[1],
                'cost': result[2]
            }
        return None

    @staticmethod
    def get_all_barcodes():
        """Get all barcode entries"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT barcode, item_name, category, default_cost FROM barcodes')
        results = cursor.fetchall()
        conn.close()
        return [{
            'barcode': row[0],
            'name': row[1],
            'category': row[2],
            'cost': row[3]
        } for row in results]

    @staticmethod
    def delete_barcode(barcode):
        """Delete a barcode entry"""
        conn = SQLiteDatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM barcodes WHERE barcode = ?', (barcode,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

# User Management
def show_login_form():
    """Display the login form"""
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not username or not password:
            st.error("Please enter both username and password")
            return
        role = AuthManager.authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Logged in as {username} ({role})")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

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

def show_barcode_management():
    """Display the barcode management section for admins"""
    st.header("🏷️ Barcode Management")
    barcodes = BarcodeManager.get_all_barcodes()
    if barcodes:
        st.dataframe(pd.DataFrame(barcodes), hide_index=True)
    barcode = st.text_input("Barcode")
    item_name = st.text_input("Item Name")
    category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Bakery", "Canned Goods", "Frozen", "Other"])
    default_cost = st.number_input("Default Cost", min_value=0.0, step=0.01)
    if st.button("Save Barcode"):
        if BarcodeManager.save_barcode(barcode, item_name, category, default_cost):
            st.success("Barcode saved successfully")
            st.experimental_rerun()
        else:
            st.error("Failed to save barcode")

# Main Application
def main():
    # Initialize database
    SQLiteDatabaseManager.initialize_database()

    # Initialize session state for authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None

    if not st.session_state.logged_in:
        st.set_page_config(page_title="Smart Grocery List", layout="wide")
        show_login_form()
        return

    # User is logged in, show the main app
    st.set_page_config(page_title="Smart Grocery List", layout="wide")
    st.title(f"Smart Grocery List Manager - Welcome {st.session_state.username}")

    # Logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.experimental_rerun()

    # Initialize other session state variables
    if "grocery_list" not in st.session_state:
        st.session_state.grocery_list = GroceryCategory("Main List")
    if "current_list_id" not in st.session_state:
        today_date = dt.date.today().strftime("%Y-%m-%d")
        st.session_state.current_list_id = today_date
        # Load today's list automatically if it exists
        if SQLiteListManager.list_exists(today_date):
            items = SQLiteListManager.load_list(today_date)
            st.session_state.grocery_list.children = items
        else:
            # Create an empty list for today
            st.session_state.grocery_list.children = []

    # Create tabs for different sections
    tabs = st.tabs([
        "📝 My Lists",
        "📊 Analytics",
        "📷 Barcode Scanner",
        "⚙️ Admin Panel" if st.session_state.role == 'admin' else "ℹ️ About"
    ])

    # Lists tab
    with tabs[0]:
        # Sidebar for list management
        col1, col2 = st.columns([1, 3])
        with col1:
            st.header("🔗 List Management")
            list_id = st.text_input("Enter/Create List ID", value=st.session_state.current_list_id)
            if st.button("Load List"):
                if list_id:
                    # Save the current list before loading a new one
                    if len(st.session_state.grocery_list.children) > 0:
                        SQLiteListManager.save_list(
                            st.session_state.current_list_id,
                            st.session_state.grocery_list.children
                        )
                    # Clear the current list completely
                    st.session_state.grocery_list.children = []
                    # Load the new list if it exists
                    if SQLiteListManager.list_exists(list_id):
                        items = SQLiteListManager.load_list(list_id)
                        st.session_state.grocery_list.children = items
                    else:
                        st.session_state.grocery_list.children = []
                    st.session_state.current_list_id = list_id
            if st.button("Save List"):
                if list_id:
                    SQLiteListManager.save_list(
                        list_id,
                        st.session_state.grocery_list.children
                    )
                    st.session_state.current_list_id = list_id

    # Barcode Scanner tab
    with tabs[2]:
        show_barcode_scanner()

    # Admin Panel tab or About tab
    with tabs[3]:
        if st.session_state.role == 'admin':
            admin_tabs = st.tabs(["User Management", "Barcode Management"])
            with admin_tabs[0]:
                show_user_management(st.session_state.username, st.session_state.role)
            with admin_tabs[1]:
                show_barcode_management()
        else:
            st.header("ℹ️ About")
            st.write("""
            ## Grocery List Manager
            This application helps you manage your grocery shopping lists.
            """)

if __name__ == "__main__":
    main()