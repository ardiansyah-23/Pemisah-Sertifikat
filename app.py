import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile

st.title("PDF Auto-Splitter & Renamer")

# Membaca file template.xlsx yang ada di luar app.py
with open("template.xlsx", "rb") as file:
    btn = st.download_button(
        label="Download Template Excel",
        data=file,
        file_name="template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# Upload file
pdf_file = st.file_uploader("Upload PDF Sertifikat", type="pdf")
excel_file = st.file_uploader("Upload Excel Daftar Nama", type="xlsx")

if pdf_file and excel_file:
    df = pd.read_excel(excel_file)
    df = pd.read_excel(excel_file)
    
    # Mencari kolom yang mengandung kata 'nama' (tidak peduli huruf besar/kecil)
    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
    
    if kolom_nama:
        nama_list = df[kolom_nama].tolist()
    else:
        # Fallback: ambil kolom pertama jika tidak ketemu kolom bernama 'nama'
        nama_list = df.iloc[:, 0].tolist()
        st.warning("Kolom 'Nama' tidak ditemukan, menggunakan kolom pertama sebagai gantinya.")
    
    reader = PdfReader(pdf_file)
    
    if st.button("Proses & Download Zip"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, nama in enumerate(nama_list):
                if i < len(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    
                    # Simpan per halaman ke buffer
                    pdf_buffer = io.BytesIO()
                    writer.write(pdf_buffer)
                    
                    # Masukkan ke dalam file zip
                    zip_file.writestr(f"{nama}.pdf", pdf_buffer.getvalue())
        
        st.download_button(
            label="Download Semua Hasil (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="hasil_split.zip",
            mime="application/zip"
        )
