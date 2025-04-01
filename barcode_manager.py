import json
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