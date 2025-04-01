import cv2
import streamlit as st

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