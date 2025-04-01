# Smart Grocery List Manager

## 🛒 Overview
The **Smart Grocery List Manager** is a Streamlit-based application designed to simplify grocery shopping and management. It allows users to create and manage grocery lists, track spending, analyze trends, and even scan barcodes to add items quickly. The app supports both regular users and admin users with role-based access.

---

## ✨ Features
- **Grocery List Management**: Create, edit, and save multiple grocery lists.
- **Barcode Scanning**: Quickly add items to your list by scanning barcodes.
- **Analytics**: View monthly spending trends and category-wise breakdowns.
- **Admin Panel**: Manage users and barcode databases (admin-only).
- **Voice Input**: Add items to your list using voice commands.
- **Export Options**: Export grocery lists as PDF files.
- **Role-Based Access**: Separate functionalities for regular users and admins.

---

## 🛠️ Setup Instructions

### Prerequisites
1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Dependencies**: Install required Python packages using `pip`.

### Installation
1. Clone the repository or download the project files.
2. Navigate to the project directory:
   ```bash
   cd "c:\Users\Manikanta\OneDrive\Desktop\MyCourses_files\textbooks\Projects\Para Project"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```
2. Open the app in your browser at `http://localhost:8501`.

---

## 📂 Project Structure
- **`main.py`**: The main entry point of the application.
- **`auth_manager.py`**: Handles user authentication and role management.
- **`database_manager.py`**: Manages SQLite database operations.
- **`grocery_components.py`**: Defines classes for grocery categories and items.
- **`barcode_manager.py`**: Handles barcode-related operations.
- **`helpers.py`**: Contains utility functions like voice input handling and PDF generation.
- **`barcode_scanner.py`**: Provides barcode scanning functionality.
- **`grocery_app.py`**: Contains additional app functionalities like user management.

---

## 🚀 Usage
1. **Login**: Use your credentials to log in. Admin users have additional privileges.
2. **Navigation**: Use the sidebar to switch between tabs:
   - **My Lists**: Manage your grocery lists.
   - **Analytics**: View spending trends and category breakdowns.
   - **Barcode Scanner**: Scan barcodes to add items.
   - **Admin Panel**: Manage users and barcodes (admin-only).
   - **About**: Learn more about the app.
3. **Quick Actions**: Use the sidebar for quick actions like logout or app reload.

---

## 🛡️ User Roles
- **Regular Users**:
  - Create and manage grocery lists.
  - Add items manually or via barcode/voice input.
  - View analytics for personal spending.
- **Admin Users**:
  - Manage users and barcodes.
  - Access all regular user functionalities.

---

## 📊 Analytics
- **Monthly Spending Trends**: Visualize total spending per month.
- **Category Distribution**: Analyze spending and item counts by category.
- **Export Data**: Download lists and analytics as PDF files.

---

## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📧 Support
For any issues or questions, please contact the project administrator.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.