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

# ------------------------------
# SQLite Database Configuration
# ------------------------------
DB_NAME = "grocery.db"

# ------------------------------
# Database Manager Class
# ------------------------------
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
        ''')
        conn.commit()
        conn.close()

# ------------------------------
# Composite Pattern Implementation
# ------------------------------
class GroceryComponent(ABC):
    @abstractmethod
    def display(self):
        pass

class GroceryItem(GroceryComponent):
    def __init__(self, name, category, cost=None, mfg_date=None, exp_date=None):
        self.name = name
        self.category = category
        self.cost = cost
        self.mfg_date = mfg_date
        self.exp_date = exp_date

    def display(self):
        item_info = f"{self.name} ({self.category})"
        if self.cost:
            item_info += f" - ${self.cost}"
        if self.mfg_date:
            item_info += f" - Mfg: {self.mfg_date}"
        if self.exp_date:
            item_info += f" - Exp: {self.exp_date}"
        return item_info

class GroceryCategory(GroceryComponent):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def display(self):
        result = []
        for child in self.children:
            result.append(child.display())
        return result

# ------------------------------
# Modified Database Operations
# ------------------------------
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
            'exp_date': item.exp_date
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
                item.get('exp_date')
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

# ------------------------------
# Helper Classes
# ------------------------------
class VoiceInputHandler:
    @staticmethod
    def listen_for_items():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except:
                return None

class PDFReport:
    @staticmethod
    def generate_report(items):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Calculate total cost
        total_cost = 0
        for item in items:
            if item.cost is not None:
                total_cost += float(item.cost)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Grocery List Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Generated on: {st.session_state.get('current_list_id', 'Unnamed List')}")
        
        # Header
        y_position = 700
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Item")
        c.drawString(150, y_position, "Category")
        c.drawString(250, y_position, "Cost")
        c.drawString(300, y_position, "Mfg Date")
        c.drawString(380, y_position, "Exp Date")
        
        # Line under header
        y_position -= 5
        c.line(50, y_position, 500, y_position)
        y_position -= 15
        
        # Items
        c.setFont("Helvetica", 10)
        for i, item in enumerate(items):
            c.drawString(50, y_position, f"{i+1}. {item.name}")
            c.drawString(150, y_position, item.category)
            c.drawString(250, y_position, f"${item.cost}" if item.cost else "-")
            c.drawString(300, y_position, item.mfg_date if item.mfg_date else "-")
            c.drawString(380, y_position, item.exp_date if item.exp_date else "-")
            
            y_position -= 20
            
            # New page if needed
            if y_position < 70:  # Increased to make room for totals
                c.showPage()
                y_position = 750
                
                # Header on new page
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y_position, "Item")
                c.drawString(150, y_position, "Category")
                c.drawString(250, y_position, "Cost")
                c.drawString(300, y_position, "Mfg Date")
                c.drawString(380, y_position, "Exp Date")
                
                # Line under header
                y_position -= 5
                c.line(50, y_position, 500, y_position)
                y_position -= 15
                c.setFont("Helvetica", 10)
        
        # Final line
        y_position -= 5
        c.line(50, y_position, 500, y_position)
        y_position -= 15
        
        # Summary information
        c.drawString(50, y_position, f"Total Items: {len(items)}")
        y_position -= 20
        c.drawString(50, y_position, f"Total Cost: ${total_cost:.2f}")
            
        c.save()
        buffer.seek(0)
        return buffer

# ------------------------------
# Main Application
# ------------------------------
def main():
    # Initialize database
    SQLiteDatabaseManager.initialize_database()
    
    st.set_page_config(page_title="Smart Grocery List", layout="wide")
    st.title("🛒 SQLite Grocery List Manager")

    # Initialize session state
    if "grocery_list" not in st.session_state:
        st.session_state.grocery_list = GroceryCategory("Main List")
    
    # Set the default list ID as today's date
    today_date = dt.date.today().strftime("%Y-%m-%d")
    
    if "current_list_id" not in st.session_state:
        st.session_state.current_list_id = today_date
        # Load today's list automatically if it exists
        if SQLiteListManager.list_exists(today_date):
            items = SQLiteListManager.load_list(today_date)
            st.session_state.grocery_list.children = items
        else:
            # Create an empty list for today
            st.session_state.grocery_list.children = []
    
    if "voice_input" not in st.session_state:
        st.session_state.voice_input = None

    # Sidebar for list management
    with st.sidebar:
        st.header("🔗 List Management")
        list_id = st.text_input("Enter/Create List ID", value=today_date)
        
        # Show warning if trying to view a different list
        if list_id != st.session_state.current_list_id:
            st.warning("⚠️ You're trying to access a different list. Click 'Load List' to switch.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Load List"):
                if list_id:
                    # Save the current list before loading a new one
                    if len(st.session_state.grocery_list.children) > 0:
                        SQLiteListManager.save_list(
                            st.session_state.current_list_id,
                            st.session_state.grocery_list.children
                        )
                        st.success(f"Saved current list '{st.session_state.current_list_id}' before switching")
                    
                    # Clear the current list completely
                    st.session_state.grocery_list.children = []
                    
                    # Load the new list if it exists
                    if SQLiteListManager.list_exists(list_id):
                        items = SQLiteListManager.load_list(list_id)
                        st.session_state.grocery_list.children = items
                        st.success(f"Loaded {len(items)} items from list '{list_id}'")
                    else:
                        st.info(f"Created new empty list '{list_id}'")
                    
                    # Update the current list ID
                    st.session_state.current_list_id = list_id
                else:
                    st.error("Please enter a List ID")
        
        with col2:
            if st.button("Save List"):
                if list_id:
                    SQLiteListManager.save_list(
                        list_id,
                        st.session_state.grocery_list.children
                    )
                    st.session_state.current_list_id = list_id
                    st.success(f"List '{list_id}' saved successfully!")
                else:
                    st.error("Please enter a List ID")
        
        # Display current list ID
        if st.session_state.current_list_id:
            st.info(f"Current List: {st.session_state.current_list_id}")
        
        # Add item form
        st.header("➕ Add Item")
        
        # Fill in the name field with voice input if available
        if st.session_state.voice_input:
            item_name = st.text_input("Item Name", value=st.session_state.voice_input)
            # Clear the voice input after using it
            if st.button("Clear Voice Input"):
                st.session_state.voice_input = None
                st.experimental_rerun()
        else:
            item_name = st.text_input("Item Name")
            
        item_category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Bakery", "Canned Goods", "Frozen", "Other"])
        
        col1, col2 = st.columns(2)
        with col1:
            item_cost = st.text_input("Cost ($)", key="cost_input")
        with col2:
            # Convert empty strings to None
            if item_cost and item_cost.strip():
                try:
                    item_cost = float(item_cost)
                except ValueError:
                    st.error("Cost must be a number")
                    item_cost = None
            else:
                item_cost = None
        
        col1, col2 = st.columns(2)
        with col1:
            mfg_date = st.date_input("Manufacturing Date", value=None, key="mfg_date")
            mfg_date_str = mfg_date.strftime("%Y-%m-%d") if mfg_date else None
        with col2:
            exp_date = st.date_input("Expiry Date", value=None, key="exp_date")
            exp_date_str = exp_date.strftime("%Y-%m-%d") if exp_date else None
        
        if st.button("Add Item"):
            if item_name:
                new_item = GroceryItem(
                    item_name, 
                    item_category, 
                    item_cost,
                    mfg_date_str,
                    exp_date_str
                )
                st.session_state.grocery_list.children.append(new_item)
                st.success(f"Added {item_name}")
                # Clear voice input after adding
                st.session_state.voice_input = None
            else:
                st.error("Please enter an item name")
        
        # Voice Input Section
        st.header("🎤 Voice Input")
        if st.button("Add Item by Voice"):
            voice_text = VoiceInputHandler.listen_for_items()
            if voice_text:
                st.session_state['voice_input'] = voice_text
                st.success(f"Voice input detected: {voice_text}")
            else:
                st.error("No voice input detected")
        
        # Debug section
        st.header("🔍 Debug")
        if st.checkbox("Show Database Contents"):
            results = SQLiteListManager.debug_list_contents()
            if results:
                for db_list_id, items_json in results:
                    with st.expander(f"List: {db_list_id}"):
                        items = json.loads(items_json)
                        st.write(f"Items count: {len(items)}")
                        st.json(items)
            else:
                st.write("No lists found in database")

    # Main content area
    
    # Display current list header
    current_list_date = st.session_state.current_list_id
    st.header(f"📝 Your Grocery List for {current_list_date}")
    
    # Always show the table structure even if empty
    st.write(f"Items in list: {len(st.session_state.grocery_list.children)}")
    
    # Display items in a table format
    if st.session_state.grocery_list.children:
        # Create a DataFrame to display in a table
        table_data = []
        for i, item in enumerate(st.session_state.grocery_list.children):
            table_data.append({
                "Index": i,
                "Item": item.name,
                "Category": item.category,
                "Cost": f"${item.cost}" if item.cost else "-",
                "Mfg Date": item.mfg_date if item.mfg_date else "-",
                "Exp Date": item.exp_date if item.exp_date else "-",
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display table
        st.dataframe(
            df[["Item", "Category", "Cost", "Mfg Date", "Exp Date"]],
            hide_index=True,
            use_container_width=True
        )
        
        # Add delete item functionality using a selectbox and button
        col1, col2 = st.columns([3, 1])
        with col1:
            items_to_select = [f"{i+1}. {item.name}" for i, item in enumerate(st.session_state.grocery_list.children)]
            if items_to_select:
                selected_item = st.selectbox("Select an item to remove:", items_to_select)
                selected_index = int(selected_item.split(".")[0]) - 1
            else:
                selected_index = None
        
        with col2:
            if selected_index is not None and st.button("Remove Selected Item"):
                st.session_state.grocery_list.children.pop(selected_index)
                st.success(f"Removed {items_to_select[selected_index].split('. ')[1]}")
                st.experimental_rerun()
    else:
        # Display single message for empty list
        st.info("No items in this list yet. Add items using the form in the sidebar.")
    
    # Export options and cost summary
    st.header("📊 Summary & Export")
    
    if st.session_state.grocery_list.children:
        # Calculate total cost
        total_cost = 0
        for item in st.session_state.grocery_list.children:
            if item.cost is not None:
                total_cost += float(item.cost)
                
        # Display cost summary
        st.metric("Total Cost", f"${total_cost:.2f}")
        
        # Export buttons
        if st.button("Export as PDF"):
            pdf_buffer = PDFReport.generate_report(st.session_state.grocery_list.children)
            st.download_button(
                "Download PDF",
                data=pdf_buffer,
                file_name="grocery_list.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Add items to see cost summary")
        st.error("Cannot export an empty list")
        
    # Monthly Cost Visualization
    st.header("📈 Monthly Cost Trends")
    
    # Get all lists from the database
    all_lists = SQLiteListManager.get_all_lists()
    
    if all_lists:
        # Create a data structure for the chart
        chart_data = []
        
        for list_id, items_json in all_lists:
            # Try to parse the list_id as a date
            # We'll assume list IDs follow the format YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', list_id):
                try:
                    # Extract year and month for grouping by splitting the string
                    year, month, _ = list_id.split('-')
                    month_year = f"{year}-{month}"
                    
                    # Calculate total cost for this list
                    items_data = json.loads(items_json)
                    list_total = sum(float(item.get('cost', 0) or 0) for item in items_data)
                    
                    chart_data.append({
                        'date': list_id,
                        'month_year': month_year,
                        'total_cost': list_total,
                        'items_count': len(items_data),
                        'items_data': items_data
                    })
                except (ValueError, TypeError):
                    # Skip if date parsing fails
                    continue
        
        if chart_data:
            # Convert to DataFrame
            df = pd.DataFrame(chart_data)
            
            # Group by month and sum costs
            monthly_costs = df.groupby('month_year')['total_cost'].sum().reset_index()
            
            # Sort by month_year
            monthly_costs = monthly_costs.sort_values('month_year')
            
            # Create bar chart for monthly costs
            fig = px.bar(
                monthly_costs, 
                x='month_year', 
                y='total_cost',
                labels={'month_year': 'Month', 'total_cost': 'Total Cost ($)'},
                title='Monthly Grocery Spending',
                color='total_cost',
                color_continuous_scale='Viridis'
            )
            
            # Format x-axis
            fig.update_xaxes(
                title_text="Month"
            )
            
            # Format y-axis to show dollar amounts
            fig.update_yaxes(
                tickprefix="$",
                title_text="Total Spending"
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Also show the data in tabular form
            with st.expander("Show Monthly Cost Data"):
                display_data = monthly_costs.copy()
                display_data['total_cost'] = display_data['total_cost'].map('${:.2f}'.format)
                
                # Add a readable month column by reformatting YYYY-MM to Month Year
                display_data['month_display'] = display_data['month_year'].apply(lambda x: 
                    f"{['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(x.split('-')[1]) - 1]} {x.split('-')[0]}")
                
                st.dataframe(display_data[['month_display', 'total_cost']], hide_index=True)
                
            # Category Distribution Chart for Selected Month
            st.subheader("📊 Category Distribution by Month")
            
            # Get unique months for selection
            unique_months = sorted(df['month_year'].unique())
            
            # Default to current month if available, otherwise first month
            default_month = None
            current_month = dt.date.today().strftime("%Y-%m")
            if current_month in unique_months:
                default_month = current_month
            else:
                default_month = unique_months[0] if unique_months else None
            
            # Month selector
            selected_month = st.selectbox(
                "Select Month to View Category Distribution:",
                options=unique_months,
                format_func=lambda x: f"{['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(x.split('-')[1]) - 1]} {x.split('-')[0]}",
                index=unique_months.index(default_month) if default_month in unique_months else 0
            )
            
            if selected_month:
                # Filter data for selected month
                selected_month_data = df[df['month_year'] == selected_month]
                
                # Collect all items for the selected month
                all_category_data = []
                
                for _, row in selected_month_data.iterrows():
                    items_data = row['items_data']
                    for item in items_data:
                        all_category_data.append({
                            'category': item.get('category', 'Uncategorized'),
                            'name': item.get('name', 'Unknown Item'),
                            'cost': float(item.get('cost', 0) or 0)
                        })
                
                if all_category_data:
                    # Create DataFrame for category analysis
                    category_df = pd.DataFrame(all_category_data)
                    
                    # Group by category
                    category_counts = category_df.groupby('category').size().reset_index(name='count')
                    category_costs = category_df.groupby('category')['cost'].sum().reset_index()
                    
                    # Merge counts and costs
                    category_analysis = pd.merge(category_counts, category_costs, on='category')
                    
                    # Sort by count (descending)
                    category_analysis = category_analysis.sort_values('count', ascending=False)
                    
                    # Create two charts side by side
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Item count by category
                        fig_count = px.pie(
                            category_analysis,
                            values='count',
                            names='category',
                            title=f'Items by Category ({selected_month})',
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        st.plotly_chart(fig_count, use_container_width=True)
                    
                    with col2:
                        # Cost by category
                        fig_cost = px.pie(
                            category_analysis,
                            values='cost',
                            names='category',
                            title=f'Spending by Category ({selected_month})',
                            color_discrete_sequence=px.colors.qualitative.Bold
                        )
                        # Format the hover text to show dollar amounts
                        fig_cost.update_traces(hovertemplate='%{label}<br>$%{value:.2f}<br>%{percent}')
                        st.plotly_chart(fig_cost, use_container_width=True)
                    
                    # Show category data in a table
                    st.subheader(f"Category Breakdown for {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(selected_month.split('-')[1]) - 1]} {selected_month.split('-')[0]}")
                    
                    # Format the cost column
                    category_analysis['cost'] = category_analysis['cost'].map('${:.2f}'.format)
                    
                    # Display the table
                    st.dataframe(
                        category_analysis.rename(columns={
                            'category': 'Category',
                            'count': 'Number of Items',
                            'cost': 'Total Cost'
                        }),
                        hide_index=True
                    )
                    
                    # Display item details
                    with st.expander("View All Items in Selected Month"):
                        # Create a detailed view of all items
                        item_detail_df = pd.DataFrame(all_category_data)
                        item_detail_df['cost'] = item_detail_df['cost'].map('${:.2f}'.format)
                        
                        st.dataframe(
                            item_detail_df.rename(columns={
                                'category': 'Category',
                                'name': 'Item',
                                'cost': 'Cost'
                            }),
                            hide_index=True
                        )
                else:
                    st.info(f"No items found for {selected_month}")
        else:
            st.info("No date-based lists found for generating the monthly cost chart.")
    else:
        st.info("Add more lists with dates as IDs to see monthly cost trends.")

if __name__ == "__main__":
    main()