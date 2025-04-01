from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import speech_recognition as sr
import streamlit as st

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
                total_cost += float(item.cost) * item.quantity
        
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
        c.drawString(300, y_position, "Quantity")
        c.drawString(350, y_position, "Total Cost")
        c.drawString(400, y_position, "Mfg Date")
        c.drawString(480, y_position, "Exp Date")
        
        # Line under header
        y_position -= 5
        c.line(50, y_position, 550, y_position)
        y_position -= 15
        
        # Items
        c.setFont("Helvetica", 10)
        for i, item in enumerate(items):
            c.drawString(50, y_position, f"{i+1}. {item.name}")
            c.drawString(150, y_position, item.category)
            c.drawString(250, y_position, f"${item.cost}" if item.cost else "-")
            c.drawString(300, y_position, str(item.quantity))
            c.drawString(350, y_position, f"${item.cost * item.quantity}" if item.cost else "-")
            c.drawString(400, y_position, item.mfg_date if item.mfg_date else "-")
            c.drawString(480, y_position, item.exp_date if item.exp_date else "-")
            
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
                c.drawString(300, y_position, "Quantity")
                c.drawString(350, y_position, "Total Cost")
                c.drawString(400, y_position, "Mfg Date")
                c.drawString(480, y_position, "Exp Date")
                
                # Line under header
                y_position -= 5
                c.line(50, y_position, 550, y_position)
                y_position -= 15
                c.setFont("Helvetica", 10)
        
        # Final line
        y_position -= 5
        c.line(50, y_position, 550, y_position)
        y_position -= 15
        
        # Summary information
        c.drawString(50, y_position, f"Total Items: {len(items)}")
        y_position -= 20
        c.drawString(50, y_position, f"Total Cost: ${total_cost:.2f}")
            
        c.save()
        buffer.seek(0)
        return buffer