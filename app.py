import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile

st.set_page_config(page_title="PDF Splitter", page_icon="📄")

st.title("📄 PDF Auto-Splitter")
st.markdown("Pisahkan file PDF menjadi beberapa bagian dan beri nama otomatis berdasarkan daftar Excel.")

st.divider()

# --- INI ADALAH TOMBOL OPSI (RADIO BUTTON) ---
st.subheader("⚙️ Pengaturan Split")
opsi_halaman = st.radio(
    "Pilih jumlah halaman PDF untuk setiap 1 nama Excel:",
    options=[1, 2, 3, 4, 5], # Anda bisa menambah angka di sini jika butuh lebih banyak
    format_func=lambda x: f"{x} Halaman",
    horizontal=True
)

# Variabel pembagi halaman akan langsung mengikuti pilihan tombol
pages_per_split = opsi_halaman

st.divider()

# --- Upload File ---
pdf_file = st.file_uploader("1. Upload File PDF", type="pdf")
excel_file = st.file_uploader("2. Upload Excel (.xlsx)", type=["xlsx", "xls"])

# --- Proses Utama ---
if pdf_file and excel_file:
    df = pd.read_excel(excel_file)
    
    # Mencari kolom nama
    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
    if kolom_nama:
        nama_list = df[kolom_nama].tolist()
    else:
        nama_list = df.iloc[:, 0].tolist()
        st.warning("⚠️ Kolom 'Nama' tidak ditemukan. Menggunakan kolom pertama.")
    
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    if st.button("🚀 Proses & Buat File ZIP"):
        with st.spinner(f"Sedang memotong PDF (Setiap file akan berisi {pages_per_split} halaman)..."):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for i, nama in enumerate(nama_list):
                    start_page = i * pages_per_split
                    end_page = start_page + pages_per_split
                    
                    if start_page < total_pages:
                        writer = PdfWriter()
                        for j in range(start_page, min(end_page, total_pages)):
                            writer.add_page(reader.pages[j])
                        
                        pdf_buffer = io.BytesIO()
                        writer.write(pdf_buffer)
                        
                        # Bersihkan nama file dari karakter yang tidak diizinkan sistem operasi
                        nama_file = str(nama).strip().replace("/", "_").replace("\\", "_")
                        zip_file.writestr(f"{nama_file}.pdf", pdf_buffer.getvalue())
            
            st.success("✅ Selesai!")
            st.download_button(
                label="📥 Download Semua Hasil (.zip)",
                data=zip_buffer.getvalue(),
                file_name="hasil_split_pdf.zip",
                mime="application/zip"
            )
