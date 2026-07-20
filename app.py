import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import os

st.set_page_config(page_title="PDF Splitter", page_icon="📄")

st.title("📄 PDF Auto-Splitter & Renamer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.subheader("📁 Template & Contoh File")

# --- Membagi tombol download jadi 2 kolom agar rapi ---
col1, col2 = st.columns(2)

with col1:
    excel_path = os.path.join(BASE_DIR, "template.xlsx")
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            st.download_button("📥 Download Template Excel", f, "template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col2:
    pdf_path = os.path.join(BASE_DIR, "contoh_sertifikat.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download Contoh PDF", f, "contoh_sertifikat.pdf", "application/pdf")

st.divider()

# --- Pengaturan Opsi Tombol Split ---
st.subheader("⚙️ Pengaturan Split")
opsi_halaman = st.radio(
    "Pilih jumlah halaman PDF untuk setiap 1 nama di Excel:",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: f"{x} Halaman",
    horizontal=True
)
pages_per_split = opsi_halaman

st.divider()

# --- Upload file ---
pdf_file = st.file_uploader("1. Upload PDF Sertifikat", type="pdf")
excel_file = st.file_uploader("2. Upload Excel Daftar Nama", type="xlsx")

# --- Proses Utama ---
if pdf_file and excel_file:
    df = pd.read_excel(excel_file)
    
    # Mencari kolom yang mengandung kata 'nama' (tidak peduli huruf besar/kecil)
    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
    
    if kolom_nama:
        nama_list = df[kolom_nama].tolist()
    else:
        # Fallback: ambil kolom pertama jika tidak ketemu kolom bernama 'nama'
        nama_list = df.iloc[:, 0].tolist()
        st.warning("⚠️ Kolom 'Nama' tidak ditemukan, menggunakan kolom pertama sebagai gantinya.")
    
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    if st.button("🚀 Proses & Download Zip", use_container_width=True):
        with st.spinner("Sedang memproses file..."):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                
                # Logika pemotongan berdasarkan tombol opsi
                for i, nama in enumerate(nama_list):
                    start_page = i * pages_per_split
                    end_page = start_page + pages_per_split
                    
                    if start_page < total_pages:
                        writer = PdfWriter()
                        
                        # Menambahkan halaman sesuai opsi (1 halaman, 2 halaman, dst)
                        for j in range(start_page, min(end_page, total_pages)):
                            writer.add_page(reader.pages[j])
                        
                        # Simpan per halaman ke buffer
                        pdf_buffer = io.BytesIO()
                        writer.write(pdf_buffer)
                        
                        # Bersihkan nama karakter khusus agar tidak error saat di-zip
                        nama_file = str(nama).strip().replace("/", "_").replace("\\", "_")
                        
                        # Masukkan ke dalam file zip
                        zip_file.writestr(f"{nama_file}.pdf", pdf_buffer.getvalue())
            
            st.success("✅ Selesai! Silakan unduh hasilnya di bawah ini.")
            
            st.download_button(
                label="📥 Download Semua Hasil (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="hasil_split.zip",
                mime="application/zip",
                use_container_width=True
            )
