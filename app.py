import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile
import os

st.title("PDF Auto-Splitter & Renamer")

import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.subheader("Template & Contoh File")

# --- Tombol Download Excel ---
excel_path = os.path.join(BASE_DIR, "template.xlsx")
if os.path.exists(excel_path):
    with open(excel_path, "rb") as f:
        st.download_button("Download Template Excel", f, "template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Tombol Download PDF Contoh ---
pdf_path = os.path.join(BASE_DIR, "contoh_sertifikat.pdf")
if os.path.exists(pdf_path):
with open(pdf_path, "rb") as f:
st.download_button("Download Contoh PDF", f, "contoh_sertifikat.pdf", "application/pdf")
        
# --- Tombol Download Excel ---
excel_path = os.path.join(BASE_DIR, "template.xlsx")
if os.path.exists(excel_path):
    with open(excel_path, "rb") as f:
        st.download_button("Download Template Excel", f, "template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# Upload file
