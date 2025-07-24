# streamlit_app.py

import streamlit as st
import win32print

def send_tspl_to_printer_windows(printer_name, tspl_data):
    printer_handle = win32print.OpenPrinter(printer_name)
    job_info = ("TSPL Print Job", None, "RAW")
    hJob = win32print.StartDocPrinter(printer_handle, 1, job_info)
    win32print.StartPagePrinter(printer_handle)
    win32print.WritePrinter(printer_handle, tspl_data.encode("latin-1"))
    win32print.EndPagePrinter(printer_handle)
    win32print.EndDocPrinter(printer_handle)
    win32print.ClosePrinter(printer_handle)
    st.success(f"✅ Sent TSPL print job to printer: {printer_name}")


def generate_tspl(label1, label2):
    def label_block(x_offset, data):
        return f"""
BARCODE {x_offset + 0},5,"128",40,1,0,2,2,"{data['barcode']}"
TEXT {x_offset + 0},50,"3",0,1,1,"{data['line1']}"
TEXT {x_offset + 0},70,"3",0,1,1,"{data['line2']}"
TEXT {x_offset + 0},90,"3",0,1,1,"{data['line3']}"
TEXT {x_offset + 0},110,"3",0,1,1,"{data['line4']}"
TEXT {x_offset + 0},140,"3",0,1,1,"MRP:"
TEXT {x_offset + 60},140,"3",0,1.5,1.5,"{data['price']}"
TEXT {x_offset + 170},20,"3",90,1,1,"Kushal's"
"""

    tspl = """
SIZE 55 mm, 21 mm
GAP 3 mm, 0
DIRECTION 1
CLS
"""
    tspl += label_block(30, label1)
    tspl += label_block(365, label2)
    tspl += "\nPRINT 1\n"
    return tspl


# 🎛️ Streamlit UI
st.title("🖨️ Dual-Label TSPL Printer - TSC TTP-345")

st.subheader("Left Label")
label1 = {
    "barcode": st.text_input("Left Barcode", "0000160124228", key="l1"),
    "line1": st.text_input("Left Line 1", "E-R Antique", key="l2"),
    "line2": st.text_input("Left Line 2", "Ruby", key="l3"),
    "line3": st.text_input("Left Line 3", "165099  40S021", key="l4"),
    "line4": st.text_input("Left Line 4", "Gold   S:NA", key="l5"),
    "price": st.text_input("Left MRP", "1020", key="l6")
}

st.subheader("Right Label")
label2 = {
    "barcode": st.text_input("Right Barcode", "0000160124228", key="r1"),
    "line1": st.text_input("Right Line 1", "E-R Antique", key="r2"),
    "line2": st.text_input("Right Line 2", "Ruby", key="r3"),
    "line3": st.text_input("Right Line 3", "165099  40S021", key="r4"),
    "line4": st.text_input("Right Line 4", "Gold   S:NA", key="r5"),
    "price": st.text_input("Right MRP", "1020", key="r6")
}

if st.button("🖨️ Print Stickers"):
    tspl_code = generate_tspl(label1, label2)
    printer_name = "TSC TTP-345"  # Make sure this matches exactly
    send_tspl_to_printer_windows(printer_name, tspl_code)
    st.code(tspl_code, language="tspl")
