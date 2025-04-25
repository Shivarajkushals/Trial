import os
import pandas as pd
import qrcode
import streamlit as st
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Simple credentials (replace with secure authentication in production)
USERNAME = "admin"
PASSWORD = "password"

def login_page():
    st.title("Login")
    
    # Create a clean login form
    with st.container():
        st.markdown("### Please login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == USERNAME and password == PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def mm(value):
    return value * 2.83465

# Function to read data from a DataFrame for Action 3
def extract_data_from_dataframe(df):
    data = {
        'split_values': {},    # For split components
        'original_values': {}  # For intact original values
    }
    data1 = {}
    unique_id = 1  # Start unique ID from 1
    counter = 1
    for column in df.columns:
        for value in df[column].dropna().unique():
            # Create a unique ID for each row
            id_str = f"ID-{unique_id}" # Unique ID format
            id_str1 = str(counter)
            data1[id_str1] = str(value)
            counter += 1
            unique_id += 1

            # Store the original value
            data['original_values'][id_str] = value
                    
            # Store the split components
            components = value.split('-')
            data['split_values'][id_str] = [component.strip() for component in components]

    return data1, data

def create_qr_code(data, size_mm):
    """Generate QR code and return it as a reportlab-compatible image reader"""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to desired size in pixels (assuming 300 DPI)
    size_pixels = int(mm(size_mm) * 300 / 72)  # Convert mm to pixels at 300 DPI
    qr_image = qr_image.resize((size_pixels, size_pixels), Image.Resampling.LANCZOS)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    qr_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return ImageReader(img_byte_arr)

# Function to save data to a PDF for Action 3
def save_to_pdf(data):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the custom TTF font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"  # Provide the correct path to your .ttf file
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))  # Register the font

    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))  # Use the BytesIO buffer
    width, height = landscape(A3)
    x_offset = mm(19.40)
    y_offset = height - mm(14.11)
    compartment_width = mm(24.70)  # Width of each compartment
    compartment_height = mm(24)  # Height of each compartment
    margin_between_entities = mm(3)  # Margin between entities
    static_strings = ["Rack", "Level", "Position"]  # Static labels

    pdf.setLineWidth(mm(0.035))  # Set border thickness

    for unique_id in data['split_values'].keys():
        components = data['split_values'][unique_id]  # Get split components for this ID
        original_value = data['original_values'][unique_id]
        
        total_width = len(static_strings) * compartment_width

        # Draw background rectangles first
        for i in range(len(static_strings)):
            compartment_x = x_offset + i * compartment_width
            pdf.setFillColor(colors.HexColor("#2633cf"))
            pdf.rect(compartment_x, y_offset - compartment_height, compartment_width, compartment_height, fill=1)

        # Draw static strings on top of the background
        for i, static_string in enumerate(static_strings):
            compartment_x = x_offset + i * compartment_width
            pdf.setFont("Mitr-SemiBold", mm(3.2))
            pdf.setFillColor(colors.HexColor("#b3b3b3"))
            text_width = pdf.stringWidth(static_string, "Mitr-SemiBold", mm(3.2))
            pdf.drawString(compartment_x + (compartment_width - text_width) / 2, 
                           y_offset - compartment_height + mm(1.76), static_string)

        # Draw dynamic components on top of the background
        for i, component in enumerate(components):
            if i < len(static_strings):
                compartment_x = x_offset + i * compartment_width
                pdf.setFont("Mitr-SemiBold", mm(16.92))
                pdf.setFillColor(colors.HexColor("#b3b3b3"))
                text_width = pdf.stringWidth(component, "Mitr-SemiBold", mm(16.92))
                pdf.drawString(compartment_x + (compartment_width - text_width) / 2, 
                               y_offset - compartment_height + mm(7.76), component)

        # Move the x_offset for the next entity
        x_offset += total_width + margin_between_entities
        if x_offset + total_width > width:
            y_offset -= compartment_height + margin_between_entities
            x_offset = mm(19.40)

        if y_offset < mm(17.63):
            pdf.showPage()
            pdf.setPageSize(landscape(A3))
            pdf.setLineWidth(mm(0.035))
            x_offset = mm(19.40)
            y_offset = height - mm(14.11)

    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data


def save_to_pdf1(data):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the custom TTF font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"  # Provide the correct path to your .ttf file
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))  # Register the font

    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))  # Use the BytesIO buffer
    width, height = landscape(A3)
    x_offset = mm(19.40)
    y_offset = height - mm(14.11)
    compartment_width = mm(24.70)  # Width of each compartment
    compartment_height = mm(24)  # Height of each compartment
    margin_between_entities = mm(2.99)  # Margin between entities
    static_strings = ["Rack", "Level", "Position"]  # Static labels

    pdf.setLineWidth(mm(0.035))  # Set border thickness

    for unique_id in data['split_values'].keys():
        components = data['split_values'][unique_id]  # Get split components for this ID
        original_value = data['original_values'][unique_id]
        
        # Calculate total width of the entity (compartments)
        total_width = len(static_strings) * compartment_width

        # Define a list of colors for compartments
        compartment_colors = [
            colors.HexColor("#D8E1F1"),  # Color for the first compartment
            colors.HexColor("#E1E101"),  # Color for the second compartment
            colors.HexColor("#E2EFD8"),  # Color for the third compartment
        ]
        
        # Draw background rectangles with different colors
        for i in range(len(static_strings)):
            compartment_x = x_offset + i * compartment_width  # Calculate x position for each compartment
            
            # Set the fill color dynamically based on the compartment index
            pdf.setFillColor(compartment_colors[i % len(compartment_colors)])  # Use modulo to loop through colors
            pdf.rect(compartment_x, y_offset - compartment_height, compartment_width, compartment_height, fill=1)  # Fill the rectangle


        # Draw static strings on top of the background
        for i, static_string in enumerate(static_strings):
            compartment_x = x_offset + i * compartment_width  # Calculate x position for each compartment
            
            # Set font and size for the static component inside the compartment
            pdf.setFont("Mitr-SemiBold", mm(3.2))  # Font size for static strings
            pdf.setFillColor(colors.HexColor("#000000"))  # Set to 30% gray
            text_width = pdf.stringWidth(static_string, "Mitr-SemiBold", mm(3.2))
            pdf.drawString(compartment_x + (compartment_width - text_width) / 2, 
                           y_offset - compartment_height + mm(1.76), static_string)  # Adjusted vertical position

        # Draw dynamic components on top of the background
        for i, component in enumerate(components):
            if i < len(static_strings):  # Ensure we only draw components where static strings exist
                compartment_x = x_offset + i * compartment_width  # Calculate x position for each compartment

                # Set font and size for dynamic components using the custom font
                pdf.setFont("Mitr-SemiBold", mm(16.92))  # Use the custom font
                pdf.setFillColor(colors.HexColor("#000000"))  # Set to white
                text_width = pdf.stringWidth(component, "Mitr-SemiBold", mm(16.92))
                pdf.drawString(compartment_x + (compartment_width - text_width) / 2, 
                               y_offset - compartment_height + mm(7.76), component)

        # Move the x_offset for the next entity 
        x_offset += total_width + margin_between_entities  # Add margin after the current entity

        # Reset x_offset if it exceeds the page width
        if x_offset + total_width > width:
            y_offset -= compartment_height + margin_between_entities  # Move down for the next row of entities
            x_offset = mm(19.40)  # Reset x offset

        if y_offset < mm(17.63):  # Create a new page if the height limit is reached
            pdf.showPage()  # Finalize the current page
            pdf.setPageSize(landscape(A3))  # Set page size to landscape A3
            pdf.setLineWidth(mm(0.035))  # Set border thickness
            x_offset = mm(19.40)  # Reset x offset
            y_offset = height - mm(14.11)  # Reset y offset

    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data

def save_to_pdf2(data):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the custom TTF font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))

    # Initialize PDF with A3 landscape
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))
    page_width, page_height = landscape(A3)
    
    # Initialize starting positions
    x_start = mm(19.40)
    x_offset = x_start
    y_offset = page_height - mm(14.11)
    
    # Define fixed dimensions
    compartment_height = mm(24)
    margin_between_entities = mm(2.99)
    static_strings = ["", "Rack", "Level", "Position", ""]
    qr_size = mm(21)  # QR code size in points
    
    # Define fixed compartment widths
    compartment_widths = [mm(26), mm(24.70), mm(24.70), mm(24.70), mm(10)]
    total_entity_width = sum(compartment_widths)
    
    # Define colors
    compartment_colors = [
        colors.HexColor("#FFFFFF"),
        colors.HexColor("#D8E1F1"),
        colors.HexColor("#E1E101"),
        colors.HexColor("#E2EFD8"),
        colors.HexColor("#FFF2CD"),
    ]

    # Set initial line width
    pdf.setLineWidth(mm(0.035))

    for unique_id in data['split_values'].keys():
        components = data['split_values'][unique_id]  # Get split components for this ID
        original_value = data['original_values'][unique_id]
        
        # Check if we need to start a new row
        if x_offset + total_entity_width > page_width - mm(19.40):
            x_offset = x_start
            y_offset -= compartment_height + margin_between_entities

        # Check if we need a new page
        if y_offset < mm(17.63):
            pdf.showPage()
            pdf.setPageSize(landscape(A3))
            pdf.setLineWidth(mm(0.035))
            x_offset = x_start
            y_offset = page_height - mm(14.11)

        # Draw compartments
        current_x = x_offset
        for i, width in enumerate(compartment_widths):
            # Draw background
            pdf.setFillColor(compartment_colors[i])
            pdf.rect(current_x, y_offset - compartment_height, width, compartment_height, fill=1)

            # Draw static string
            pdf.setFillColor(colors.HexColor("#000000"))
            pdf.setFont("Mitr-SemiBold", mm(3.2))
            static_text = static_strings[i]
            text_width = pdf.stringWidth(static_text, "Mitr-SemiBold", mm(3.2))
            text_x = current_x + (width - text_width) / 2
            pdf.drawString(text_x, y_offset - compartment_height + mm(1.76), static_text)

            # Add QR code in the first compartment
            if i == 0:
                # Generate QR code and get ImageReader object
                qr_image = create_qr_code(original_value, size_mm=qr_size / mm(1))
                # Calculate center position for QR code
                qr_x = current_x + (width - qr_size) / 2
                qr_y = y_offset - compartment_height + (compartment_height - qr_size) / 2
                # Draw QR code
                pdf.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
                
            if i == 4:
                arrow = "↑"
                pdf.setFont("Mitr-SemiBold", mm(14))  # Adjust font size to fit 10mm compartment
                arrow_width = pdf.stringWidth(arrow, "Mitr-SemiBold", mm(14))
                arrow_x = current_x + (width - arrow_width) / 2
                arrow_y = y_offset - compartment_height + mm(6)  # Adjusted position for centered arrow
                pdf.setFillColor(colors.HexColor("#000000"))
                pdf.drawString(arrow_x, arrow_y, arrow)

            # Draw component - starting from the second compartment (index 1)
            if 1 <= i < len(components) + 1:
                pdf.setFont("Mitr-SemiBold", mm(16.93))
                component_text = components[i - 1]
                text_width = pdf.stringWidth(component_text, "Mitr-SemiBold", mm(16.93))
                text_x = current_x + (width - text_width) / 2
                pdf.drawString(text_x, y_offset - compartment_height + mm(7.76), component_text)

            current_x += width

        # Move x_offset for next entity
        x_offset += total_entity_width + margin_between_entities

    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data

def save_to_pdf3(data1):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))

    # Initialize PDF with A3 landscape
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))
    page_width, page_height = landscape(A3)
    
    # Initialize positions
    x_start = mm(9.5)
    y_start = page_height - mm(14.11)
    
    # Define dimensions
    qr_box_width = mm(40)
    qr_box_height = mm(46)
    margin = mm(5)
    qr_size = mm(35)
    
    x_offset = x_start
    y_offset = y_start
    
    for unique_id, value in data1.items():
        # Check if we need to start a new row
        if x_offset + qr_box_width > page_width - x_start:
            x_offset = x_start
            y_offset -= qr_box_height + margin
            
        # Check if we need a new page
        if y_offset - qr_box_height < mm(14.11):
            pdf.showPage()
            pdf.setPageSize(landscape(A3))
            x_offset = x_start
            y_offset = y_start
            
        # Draw box
        pdf.rect(x_offset, y_offset - qr_box_height, qr_box_width, qr_box_height)
        
        # Add QR code
        qr_image = create_qr_code(value, size_mm=qr_size / mm(1))  # QR code contains the ID number
        qr_x = x_offset + (qr_box_width - qr_size) / 2
        qr_y = y_offset - qr_box_height + mm(9.5)
        pdf.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Draw separator line
        line_y = y_offset - qr_box_height + mm(8)  # Position between QR and text
        pdf.line(x_offset, line_y, x_offset + qr_box_width, line_y)
        
        # Set the fill color and draw the rectangle for background
        pdf.setFillColor(colors.HexColor("#FF6700"))  # Set background color
        pdf.rect(x_offset, line_y - mm(8), qr_box_width, mm(8), fill=1)  # Fill the rectangle
        
        # Add value text below QR code
        pdf.setFont("Mitr-SemiBold", 23)
        pdf.setFillColor(colors.HexColor("#000000"))  # Set to blue
        text_width = pdf.stringWidth(value, "Mitr-SemiBold", 23)
        text_x = x_offset + (qr_box_width - text_width) / 2
        text_y = y_offset - qr_box_height + mm(1.5)  # Adjusted to be below the line
        pdf.drawString(text_x, text_y, value)
        
        x_offset += qr_box_width + margin
    
    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data

def save_to_pdf4(data1):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))

    # Initialize PDF with A3 landscape
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))
    page_width, page_height = landscape(A3)
    
    # Initialize positions
    x_start = mm(9.5)
    y_start = page_height - mm(14.11)
    
    # Define dimensions
    qr_box_width = mm(34)
    qr_box_height = mm(66)
    margin = mm(5)
    qr_size = mm(25)
     
    x_offset = x_start
    y_offset = y_start
    
    for unique_id, value in data1.items():
        # Check if we need to start a new row
        if x_offset + qr_box_width > page_width - x_start:
            x_offset = x_start
            y_offset -= qr_box_height + margin
            
        # Check if we need a new page
        if y_offset - qr_box_height < mm(14.11):
            pdf.showPage()
            pdf.setPageSize(landscape(A3))
            x_offset = x_start
            y_offset = y_start
            
        # Draw box
        pdf.rect(x_offset, y_offset - qr_box_height, qr_box_width, qr_box_height)
        pdf.rect(x_offset + mm(2), y_offset - qr_box_height + mm(29.5), qr_box_width - mm(4), qr_box_height - mm(31.5))
        pdf.rect(x_offset + mm(2), y_offset - qr_box_height + mm(1.5), qr_box_width - mm(4), qr_box_height - mm(39.5))
        
        # Draw the background rectangle
        pdf.setFillColor(colors.HexColor("#E2EFDB"))  # Set background color
        pdf.rect(x_offset + mm(2), y_offset - qr_box_height + mm(1.5), qr_box_width - mm(4), qr_box_height - mm(39.5), fill=1)  # Fill the rectangle
        
        # Add the last letter of the value string inside the background rectangle
        if value:  # Ensure the string is not empty
            last_letter = value[-1]
            pdf.setFont("Mitr-SemiBold", 100)  # Adjust font size for better visibility
            pdf.setFillColor(colors.HexColor("#000000"))  # Set text color
            last_letter_x = x_offset + qr_box_width / 2  # Center horizontally
            last_letter_y = y_offset - qr_box_height + mm(2.5)  # Adjust vertical position within the rectangle
            pdf.drawCentredString(last_letter_x, last_letter_y, last_letter)
        
        # Add QR code
        qr_image = create_qr_code(value, size_mm=qr_size / mm(1))  # QR code contains the ID number
        qr_x = x_offset + (qr_box_width - qr_size) / 2
        qr_y = y_offset - qr_box_height + mm(37)
        pdf.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
                
        # Add value text below QR code
        pdf.setFont("Mitr-SemiBold", 12)
        pdf.setFillColor(colors.HexColor("#000000"))  # Set to blue
        text_width = pdf.stringWidth(value, "Mitr-SemiBold", 12)
        text_x = x_offset + (qr_box_width - text_width) / 2
        text_y = y_offset - qr_box_height + mm(31.5)  # Adjusted to be below the line
        pdf.drawString(text_x, text_y, value)
        
        x_offset += qr_box_width + margin
    
    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data

def save_to_pdf5(data1):
    
    # Create a BytesIO buffer to save the PDF in memory
    pdf_buffer = BytesIO()
    
    # Register the font
    font_path = "https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Mitr-SemiBold.ttf"
    pdfmetrics.registerFont(TTFont('Mitr-SemiBold', font_path))

    # Initialize PDF with A3 landscape
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(A3))
    page_width, page_height = landscape(A3)
    
    # Initialize positions
    x_start = mm(9.5)
    y_start = page_height - mm(14.11)
    
    # Define dimensions
    qr_box_width = mm(40)
    qr_box_height = mm(46)
    margin = mm(5)
    qr_size = mm(35)
    
    x_offset = x_start
    y_offset = y_start
    
    for unique_id, value in data1.items():
        # Check if we need to start a new row
        if x_offset + qr_box_width > page_width - x_start:
            x_offset = x_start
            y_offset -= qr_box_height + margin
            
        # Check if we need a new page
        if y_offset - qr_box_height < mm(14.11):
            pdf.showPage()
            pdf.setPageSize(landscape(A3))
            x_offset = x_start
            y_offset = y_start
            
        # Draw box
        pdf.rect(x_offset, y_offset - qr_box_height, qr_box_width, qr_box_height)
        
        # Add QR code
        qr_image = create_qr_code(value, size_mm=qr_size / mm(1))  # QR code contains the ID number
        qr_x = x_offset + (qr_box_width - qr_size) / 2
        qr_y = y_offset - qr_box_height + mm(9.5)
        pdf.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Draw separator line
        line_y = y_offset - qr_box_height + mm(8)  # Position between QR and text
        pdf.line(x_offset, line_y, x_offset + qr_box_width, line_y)
        
        # Set the fill color and draw the rectangle for background
        pdf.setFillColor(colors.HexColor("#FFD700"))  # Set background color
        pdf.rect(x_offset, line_y - mm(8), qr_box_width, mm(8), fill=1)  # Fill the rectangle
        
        # Add value text below QR code
        pdf.setFont("Mitr-SemiBold", 23)
        pdf.setFillColor(colors.HexColor("#000000"))  # Set to blue
        text_width = pdf.stringWidth(value, "Mitr-SemiBold", 23)
        text_x = x_offset + (qr_box_width - text_width) / 2
        text_y = y_offset - qr_box_height + mm(1.5)  # Adjusted to be below the line
        pdf.drawString(text_x, text_y, value)
        
        x_offset += qr_box_width + margin
    
    pdf.save()
    pdf_buffer.seek(0)  # Move to the beginning of the BytesIO buffer
    return pdf_buffer.getvalue()  # Return the PDF data

def main():
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.title("PDF Generator")

    st.subheader("The file expected to load should have a single column of data in first column with a header")
    
    uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)
    
    # Sidebar for button inputs
    st.sidebar.header("Choose Actions")

    # Initialize session state variables
    if 'show_generate_pdf_action1' not in st.session_state:
        st.session_state.show_generate_pdf_action1 = False
    if 'show_generate_pdf_action2' not in st.session_state:
        st.session_state.show_generate_pdf_action2 = False
    if 'show_generate_pdf_action3' not in st.session_state:
        st.session_state.show_generate_pdf_action3 = False
    if 'show_generate_pdf_action4' not in st.session_state:
        st.session_state.show_generate_pdf_action4 = False
    if 'show_generate_pdf_action5' not in st.session_state:
        st.session_state.show_generate_pdf_action5 = False
    if 'show_generate_pdf_action6' not in st.session_state:
        st.session_state.show_generate_pdf_action6 = False

    # Action 1
    if st.sidebar.button("Sticker 1", key="action1_button"):
        st.session_state.show_generate_pdf_action1 = True
        st.session_state.show_generate_pdf_action2 = False
        st.session_state.show_generate_pdf_action3 = False
        st.session_state.show_generate_pdf_action4 = False
        st.session_state.show_generate_pdf_action5 = False
        st.session_state.show_generate_pdf_action6 = False
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Sticker.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action1:
        if st.button("Generate PDF for Sticker 1", key="generate_pdf_button_1"):
            if uploaded_files:    
                data = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:  # Excel file
                        df = pd.read_excel(uploaded_file)
    
                    # Correctly unpack the tuple returned by extract_data_from_dataframe
                    _, file_data = extract_data_from_dataframe(df)
                    data.update(file_data)
    
                if data:
                    pdf_bytes = save_to_pdf(data)
                    st.success("PDF successfully generated for Sticker 1!")
                    st.download_button(
                        label="Download PDF for Sticker 1",
                        data=pdf_bytes,
                        file_name="Sticker.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.warning("No data extracted from the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")
    
    # Action 2
    if st.sidebar.button("Sticker 2", key="action2_button"):
        st.session_state.show_generate_pdf_action1 = False
        st.session_state.show_generate_pdf_action2 = True
        st.session_state.show_generate_pdf_action3 = False
        st.session_state.show_generate_pdf_action4 = False
        st.session_state.show_generate_pdf_action5 = False
        st.session_state.show_generate_pdf_action6 = False
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Colored%20Sticker.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action2:
        if st.button("Generate PDF for Sticker 2", key="generate_pdf_button_2"):
            if uploaded_files:    
                data = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)

                    _, file_data = extract_data_from_dataframe(df)
                    data.update(file_data)
                    
                if data:
                    pdf_bytes = save_to_pdf1(data)
                    st.success("PDF successfully generated for Sticker 2!")
                    st.download_button(
                        label="Download PDF for Sticker 2",
                        data=pdf_bytes,
                        file_name="Colored sticker.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("No valid data found in the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")
                
    # Action 3
    if st.sidebar.button("Sticker 3", key="action3_button"):
        st.session_state.show_generate_pdf_action1 = False
        st.session_state.show_generate_pdf_action2 = False
        st.session_state.show_generate_pdf_action3 = True
        st.session_state.show_generate_pdf_action4 = False
        st.session_state.show_generate_pdf_action5 = False
        st.session_state.show_generate_pdf_action6 = False
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Qr%20%2B%20Sticker.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action3:
        if st.button("Generate PDF for Sticker 3", key="generate_pdf_button_3"):
            if uploaded_files:    
                data = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)

                    _, file_data = extract_data_from_dataframe(df)
                    data.update(file_data)
                    
                if data:
                    pdf_bytes = save_to_pdf2(data)
                    st.success("PDF successfully generated for Sticker 3!")
                    st.download_button(
                        label="Download PDF for Sticker 3",
                        data=pdf_bytes,
                        file_name="Qr + Sticker.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("No valid data found in the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")
                
    # Action 4
    if st.sidebar.button("Sticker 4", key="action4_button"):
        st.session_state.show_generate_pdf_action1 = False
        st.session_state.show_generate_pdf_action2 = False
        st.session_state.show_generate_pdf_action3 = False
        st.session_state.show_generate_pdf_action4 = True
        st.session_state.show_generate_pdf_action5 = False
        st.session_state.show_generate_pdf_action6 = False
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Qr.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action4:
        if st.button("Generate PDF for Sticker 4", key="generate_pdf_button_4"):
            if uploaded_files:
                data1 = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
    
                    data1_part, _ = extract_data_from_dataframe(df)
                    data1.update(data1_part)
    
                if data1:
                    pdf_bytes = save_to_pdf3(data1)
                    st.success("PDF successfully generated for Sticker 4!")
                    st.download_button(
                        label="Download PDF for Sticker 4",
                        data=pdf_bytes,
                        file_name="Qr_orange_label.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("No valid data found in the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")
                
    # Action 5
    if st.sidebar.button("Sticker 5", key="action5_button"):
        st.session_state.show_generate_pdf_action1 = False
        st.session_state.show_generate_pdf_action2 = False
        st.session_state.show_generate_pdf_action3 = False
        st.session_state.show_generate_pdf_action4 = False
        st.session_state.show_generate_pdf_action5 = True
        st.session_state.show_generate_pdf_action6 = False
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Qr%20Alpha.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action5:
        if st.button("Generate PDF for Sticker 5", key="generate_pdf_button_5"):
            if uploaded_files:
                data1 = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
    
                    data1_part, _ = extract_data_from_dataframe(df)
                    data1.update(data1_part)
    
                if data1:
                    pdf_bytes = save_to_pdf4(data1)
                    st.success("PDF successfully generated for Sticker 5!")
                    st.download_button(
                        label="Download PDF for Sticker 5",
                        data=pdf_bytes,
                        file_name="Qr_Alpha.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("No valid data found in the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")
                
    # Action 6
    if st.sidebar.button("Sticker 6", key="action6_button"):
        st.session_state.show_generate_pdf_action1 = False
        st.session_state.show_generate_pdf_action2 = False
        st.session_state.show_generate_pdf_action3 = False
        st.session_state.show_generate_pdf_action4 = False
        st.session_state.show_generate_pdf_action5 = False
        st.session_state.show_generate_pdf_action6 = True
        
    st.sidebar.image("https://raw.githubusercontent.com/Shivarajkushals/Trial/main/Qr.png", use_container_width=True)

    if st.session_state.show_generate_pdf_action4:
        if st.button("Generate PDF for Sticker 6", key="generate_pdf_button_6"):
            if uploaded_files:
                data1 = {}
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
    
                    data1_part, _ = extract_data_from_dataframe(df)
                    data1.update(data1_part)
    
                if data1:
                    pdf_bytes = save_to_pdf5(data1)
                    st.success("PDF successfully generated for Sticker 6!")
                    st.download_button(
                        label="Download PDF for Sticker 6",
                        data=pdf_bytes,
                        file_name="Qr_New_label.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("No valid data found in the uploaded files.")
            else:
                st.error("Please upload at least one CSV or Excel file.")

if __name__ == "__main__":
    main()
