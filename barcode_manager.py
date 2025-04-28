import cv2
import streamlit as st
from database_manager import SQLiteDatabaseManager

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
        
        return [
            {
                'barcode': row[0],
                'name': row[1],
                'category': row[2],
                'cost': row[3]
            }
            for row in results
        ]

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
class BarcodeScanner:
    @staticmethod
    def scan_barcode():
        """Access the camera and scan a barcode using OpenCV QRCodeDetector"""
        st.write("Starting camera for barcode scanning...")
        cap = cv2.VideoCapture(0)  # Open the default camera
        detector = cv2.QRCodeDetector()  # Initialize QRCodeDetector

        barcode_data = None
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to access the camera")
                break

            # Detect and decode the barcode/QR code
            data, _, _ = detector.detectAndDecode(frame)
            if data:
                barcode_data = data
                st.success(f"Barcode detected: {barcode_data}")
                cap.release()
                cv2.destroyAllWindows()
                return barcode_data

            # Display the camera feed in a window
            cv2.imshow("Barcode Scanner", frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        st.info("No barcode detected")
        return None