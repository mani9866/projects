import streamlit as st
import datetime as dt
from auth_manager import AuthManager
from database_manager import SQLiteDatabaseManager
from grocery_components import GroceryCategory, GroceryItem
from barcode_manager import BarcodeManager
from barcode_manager import BarcodeScanner  # Add this import
from helpers import VoiceInputHandler, PDFReport
from grocery_app import SQLiteListManager, show_user_management  # Import show_barcode_scanner and show_user_management
import pandas as pd
import plotly.express as px
import re
import json

def main():
    try:
        # Initializing database
        SQLiteDatabaseManager.initialize_database()
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return
    
    # Set up page configuration
    st.set_page_config(page_title="Smart Grocery List", layout="wide",page_icon="🛒",initial_sidebar_state="collapsed")
    # Initialize session state for authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    # Define today's date
    today_date = dt.date.today().strftime("%Y-%m-%d")
    
    # Initialize session state variables
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "My Lists"  # Default tab
    
    if "current_list_id" not in st.session_state:
        st.session_state.current_list_id = today_date  # Default to today's date
    
    if "grocery_list" not in st.session_state:
        st.session_state.grocery_list = GroceryCategory("Main List")
    
    if "voice_input" not in st.session_state:
        st.session_state.voice_input = None
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_form()
        return
    
    # User is logged in, show the main app
    st.title(f"🛒 Grocery List Manager - Welcome {st.session_state.username}")
    
    
    # Sidebar enhancements
    with st.sidebar:
        st.header("👤 User Info")
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role.capitalize()}")
        st.header("📋 Navigation")
        if st.button("📝 My Lists"):
            st.session_state.current_tab = "My Lists"
        if st.button("📊 Analytics"):
            st.session_state.current_tab = "Analytics"
        if st.session_state.role == 'admin' and st.button("⚙️ Admin Panel"):
            st.session_state.current_tab = "Admin Panel"
        if st.button("ℹ️ About"):
            st.session_state.current_tab = "About"
        st.header("⚡ Quick Actions")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
        
        if st.button("Reload App"):
            st.rerun()
    # Map selected tab to corresponding functionality
    if st.session_state.current_tab == "My Lists":
        show_my_lists(today_date)
    elif st.session_state.current_tab == "Analytics":
        show_analytics()
    elif st.session_state.current_tab == "Admin Panel" and st.session_state.role == 'admin':
        st.header("⚙️ Admin Panel")
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
        
        ### Features:
        - Create and manage multiple grocery lists
        - Track costs and categorize items
        - View spending analytics by month and category
        - Scan barcodes to quickly add items (requires admin to set up barcodes first)
        - Export lists as PDF
        
        ### User Roles:
        - **Regular Users**: Can create lists, add items, and scan barcodes
        - **Admin Users**: Can also manage users and set up barcode database
        
        ### Need Help?
        Contact your administrator for assistance.
        """)
        # Get current year
    current_year = dt.date.today().year

    # Add some space before the copyright
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Add a horizontal line as a separator
    st.markdown("<hr>", unsafe_allow_html=True)

    # Create the copyright text with current year and your name
    copyright_text = f"© {current_year} Manikanta Sai Surya. All Rights Reserved."

    # Add the copyright text with centered alignment
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; color: gray; font-size: 0.8em;">
        {copyright_text}
    </div>
    """, unsafe_allow_html=True)


def show_login_form():
    """Display the login form"""
    st.title("🔐 Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if not username or not password:
            st.error("Please enter both username and password")
            return False
        
        try:
            role = AuthManager.authenticate(username, password)
            if role:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
                return True
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Error during login: {e}")
            return False
    
    return False

def show_barcode_management():
    """Display the barcode management section for admins"""
    st.header("🏷️ Barcode Management")
    
    # Display existing barcodes
    barcodes = BarcodeManager.get_all_barcodes()
    if barcodes:
        st.subheader("Existing Barcodes")
        barcode_df = pd.DataFrame(barcodes)
        
        # Format the cost column
        barcode_df['cost'] = barcode_df['cost'].apply(lambda x: f"${x:.2f}" if x else "-")
        
        st.dataframe(
            barcode_df.rename(columns={
                'barcode': 'Barcode',
                'name': 'Item Name',
                'category': 'Category',
                'cost': 'Default Cost'
            }),
            hide_index=True
        )
    else:
        st.info("No barcodes have been added yet")
    
    # Initialize session state for scanned barcode if not already set
    if "scanned_barcode" not in st.session_state:
        st.session_state.scanned_barcode = ""

    # Form to add/update barcode
    st.subheader("Add/Update Barcode")
    barcode = st.text_input("Barcode Number", value=st.session_state.scanned_barcode, key="barcode_input")
    item_name = st.text_input("Item Name")
    category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Bakery", "Canned Goods", "Frozen", "Other"])
    default_cost = st.number_input("Default Cost ($)", min_value=0.0, step=0.01, format="%.2f")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save Barcode"):
            if not barcode or not item_name:
                st.error("Please enter both barcode and item name")
            else:
                if BarcodeManager.save_barcode(barcode, item_name, category, default_cost):
                    st.success(f"Barcode for '{item_name}' saved successfully")
                    st.session_state.scanned_barcode = ""  # Clear the scanned barcode after saving
                else:
                    st.error("Failed to save barcode")
    with col2:
        if st.button("Scan Barcode"):
            scanned_barcode = BarcodeScanner.scan_barcode()
            if scanned_barcode:
                st.session_state.scanned_barcode = scanned_barcode  # Update session state with the scanned barcode
                st.success(f"Scanned Barcode: {scanned_barcode}")
    
    if "scanned_barcode" in st.session_state and st.session_state.scanned_barcode:
        if st.button("Add Scanned Barcode to Item Name"):
            item_name = st.session_state.scanned_barcode
            st.success(f"Scanned barcode added to form: {item_name}")
            st.session_state.scanned_barcode = None
            st.rerun()
    
    # Form to delete barcode
    st.subheader("Delete Barcode")
    if barcodes:
        barcode_to_delete = st.selectbox(
            "Select Barcode to Delete",
            [f"{b['barcode']} - {b['name']}" for b in barcodes]
        )
        barcode_number = barcode_to_delete.split(" - ")[0] if barcode_to_delete else None
    else:
        st.info("No barcodes to delete")
        barcode_number = None
    
    if st.button("Delete Barcode"):
        if barcode_number:
            if BarcodeManager.delete_barcode(barcode_number):
                st.success(f"Barcode '{barcode_number}' deleted successfully")
            else:
                st.error("Failed to delete barcode")

def show_my_lists(today_date):
    """Display the My Lists tab functionality"""
    st.header("📝 My Lists")
    
    # Sidebar for list management
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.header("🔗 List Management")
        list_id = st.date_input("Enter/Create List ID", value=today_date)
        
        # Show warning if trying to view a different list
        if list_id != st.session_state.current_list_id:
            st.warning("⚠️ Click 'Load List' to switch")
        
        col1_1, col1_2, = st.columns(2)
        
        with col1_1:
            if st.button("Load List"):
                if list_id:
                    # Save the current list before loading a new one
                    if len(st.session_state.grocery_list.children) > 0:
                        SQLiteListManager.save_list(
                            st.session_state.current_list_id,
                            st.session_state.grocery_list.children
                        )
                        st.success(f"Saved current list")
                    
                    # Clear the current list completely
                    st.session_state.grocery_list.children = []
                    
                    # Load the new list if it exists
                    if SQLiteListManager.list_exists(list_id):
                        items = SQLiteListManager.load_list(list_id)
                        st.session_state.grocery_list.children = items
                        st.success(f"Loaded {len(items)} items")
                    else:
                        st.info(f"Created new list")
                    
                    # Update the current list ID
                    st.session_state.current_list_id = list_id
                else:
                    st.error("Please enter a List ID")
        
        with col1_2:
            if st.button("Save List"):
                if list_id:
                    SQLiteListManager.save_list(
                        list_id,
                        st.session_state.grocery_list.children
                    )
                    st.session_state.current_list_id = list_id
                    st.success(f"List saved!")
                else:
                    st.error("Please enter a List ID")
        
        # Display current list ID
        if st.session_state.current_list_id:
            st.info(f"Current List: {st.session_state.current_list_id}")
        
        # Add item form
        st.header("➕ Add Item")
        
        # Populate the "Item Name" field with scanned item or voice input if available
        if "scanned_item_name" in st.session_state and st.session_state.scanned_item_name:
            item_name = st.text_input("Item Name", value=st.session_state.scanned_item_name)
        elif "voice_input" in st.session_state and st.session_state.voice_input:
            item_name = st.text_input("Item Name", value=st.session_state.voice_input)
        else:
            item_name = st.text_input("Item Name")
        
        item_category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Bakery", "Canned Goods", "Frozen", "Other"])
        item_quantity = st.number_input("Quantity", min_value=1, step=1, value=1, key="quantity_input")
        item_cost = st.text_input("Cost ($)", key="cost_input")
        mfg_date = st.date_input("Manufacturing Date", value=None, key="mfg_date")
        exp_date = st.date_input("Expiry Date", value=None, key="exp_date")
        
        
        if st.button("Add Item Manually"):
            if item_name:
                new_item = GroceryItem(
                    item_name, 
                    item_category, 
                    float(item_cost) if item_cost else None,
                    mfg_date.strftime("%Y-%m-%d") if mfg_date else None,
                    exp_date.strftime("%Y-%m-%d") if exp_date else None
                )
                new_item.quantity = item_quantity
                st.session_state.grocery_list.children.append(new_item)
                st.success(f"Added {item_name} (x{item_quantity})")
                # Clear scanned item and voice input after adding
                st.session_state.scanned_item_name = None
                st.session_state.voice_input = None
            else:
                st.error("Please enter an item name")
        
        # Voice Input Section
        if st.button("🎤Add Item By Voice"):
            voice_text = VoiceInputHandler.listen_for_items()
            if voice_text:
                st.session_state.voice_input = voice_text
                st.success(f"Voice input detected: {voice_text}")
        
        if "voice_input" in st.session_state and st.session_state.voice_input:
            if st.button("Add Voice Input to Item Name"):
                item_name = st.session_state.voice_input
                st.success(f"Voice input added to form: {item_name}")
                st.session_state.voice_input = None
                st.rerun()
        
        # Barcode Scanner Section
        if st.button("📷Add Item By Scan"):
            scanned_barcode = BarcodeScanner.scan_barcode()
            if scanned_barcode:
                item_data = BarcodeManager.get_item_by_barcode(scanned_barcode)
                if item_data:
                    st.session_state.scanned_item_name = item_data['name']
                    st.session_state.scanned_item_category = item_data['category']
                    st.session_state.scanned_item_cost = item_data['cost']
                    st.success(f"Scanned item: {item_data['name']} ({item_data['category']})")
                else:
                    st.error("No item found for the scanned barcode")
        
        if "scanned_item_name" in st.session_state and st.session_state.scanned_item_name:
            if st.button("Add Scanned Item to Item Name"):
                st.success(f"Scanned item added to form: {st.session_state.scanned_item_name}")
                st.rerun()
    
    with col2:
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
                    "Quantity": getattr(item, 'quantity', 1),  # Default to 1 if not set
                    "Cost": f"${item.cost}" if item.cost else "-",
                    "Mfg Date": item.mfg_date if item.mfg_date else "-",
                    "Exp Date": item.exp_date if item.exp_date else "-",
                    "Barcode": item.barcode if hasattr(item, 'barcode') and item.barcode else "-"
                })
            
            # Create DataFrame
            df = pd.DataFrame(table_data)
            
            # Display table
            st.dataframe(
                df[["Item", "Category", "Quantity", "Cost", "Mfg Date", "Exp Date", "Barcode"]],
                hide_index=True,
                use_container_width=True
            )
            
            # Add delete item functionality using a selectbox and button
            col_a, col_b = st.columns([3, 1])
            with col_a:
                items_to_select = [f"{i+1}. {item.name}" for i, item in enumerate(st.session_state.grocery_list.children)]
                if items_to_select:
                    selected_item = st.selectbox("Select an item to remove:", items_to_select)
                    selected_index = int(selected_item.split(".")[0]) - 1
                else:
                    selected_index = None
            
            with col_b:
                if selected_index is not None and st.button("Remove Selected Item"):
                    st.session_state.grocery_list.children.pop(selected_index)
                    st.success(f"Removed {items_to_select[selected_index].split('. ')[1]}")
                    st.rerun()
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
                    total_cost += float(item.cost) * getattr(item, 'quantity', 1)
                    
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
            st.error("Cannot export an empty list as PDF add items first or load an existing list")

def show_analytics():
    """Display the Analytics tab functionality"""
    st.header("📊 Analytics")
    
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
