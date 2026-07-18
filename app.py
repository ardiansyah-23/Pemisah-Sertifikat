import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile

# Konfigurasi halaman
st.set_page_config(page_title="PDF Splitter", page_icon="📄")

st.title("📄 PDF Auto-Splitter & Renamer")
st.markdown("Pisahkan file PDF menjadi beberapa bagian dan beri nama otomatis berdasarkan daftar Excel.")

st.divider()

# --- Fitur Custom Jumlah Halaman ---
st.subheader("⚙️ Pengaturan Split")
pages_per_split = st.number_input(
    "Berapa jumlah halaman untuk setiap nama file?", 
    min_value=1, 
    value=1, 
    step=1,
    help="Contoh: Jika diisi 2, maka Baris 1 di Excel akan mendapatkan Halaman 1-2, Baris 2 mendapatkan Halaman 3-4, dst."
)

st.divider()

# --- Upload File ---
st.subheader("📥 Upload File")
col1, col2 = st.columns(2)

with col1:
    pdf_file = st.file_uploader("1. Upload File PDF", type="pdf")
with col2:
    excel_file = st.file_uploader("2. Upload Excel (.xlsx)", type=["xlsx", "xls"])

# --- Proses Utama ---
if pdf_file and excel_file:
    st.info("File berhasil diunggah. Siap untuk diproses!")
    
    # Membaca file Excel
    df = pd.read_excel(excel_file)
    
    # Mencari kolom nama secara dinamis (mengabaikan huruf besar/kecil)
    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
    
    if kolom_nama:
        nama_list = df[kolom_nama].tolist()
    else:
        nama_list = df.iloc[:, 0].tolist()
        st.warning("⚠️ Kolom 'Nama' tidak ditemukan. Menggunakan data di kolom pertama sebagai nama file.")
    
    # Membaca file PDF
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    st.write(f"- **Total nama di Excel:** {len(nama_list)} orang")
    st.write(f"- **Total halaman PDF:** {total_pages} halaman")
    
    # Tombol Eksekusi
    if st.button("🚀 Proses & Buat File ZIP", use_container_width=True):
        with st.spinner("Sedang memotong dan mengganti nama PDF..."):
            
            # Membuat wadah ZIP di dalam memori
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                
                for i, nama in enumerate(nama_list):
                    start_page = i * pages_per_split
                    end_page = start_page + pages_per_split
                    
                    if start_page < total_pages:
                        writer = PdfWriter()
                        
                        # Menambahkan halaman sesuai rentang
                        for j in range(start_page, min(end_page, total_pages)):
                            writer.add_page(reader.pages[j])
                        
                        # Menyimpan PDF sementara di memori
                        pdf_buffer = io.BytesIO()
                        writer.write(pdf_buffer)
                        
                        # Memasukkan PDF ke dalam ZIP
                        # Pastikan nama file valid (hapus karakter aneh jika perlu)
                        nama_file_bersih = str(nama).strip().replace("/", "_").replace("\\", "_")
                        zip_file.writestr(f"{nama_file_bersih}.pdf", pdf_buffer.getvalue())
            
            st.success("✅ Proses berhasil! Silakan unduh hasilnya di bawah ini.")
            
            # Tombol Download
            st.download_button(
                label="📥 Download Semua Hasil (.zip)",
                data=zip_buffer.getvalue(),
                file_name="hasil_split_pdf.zip",
                mime="application/zip",
                use_container_width=True
            )
