import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import os

st.set_page_config(page_title="PDF Splitter & Token System", page_icon="📄")

# --- SIMULASI DATABASE TOKEN (Di aplikasi nyata, hubungkan ke Database/API Backend) ---
if 'token_db' not in st.session_state:
    st.session_state.token_db = {
        "PROMO2026": {"max_uses": 3, "used_count": 0},
        "VIPUSER": {"max_uses": 10, "used_count": 0}
    }

# --- STATE UNTUK STATUS LOGIN/TOKEN ---
if 'token_verified' not in st.session_state:
    st.session_state.token_verified = False
    st.session_state.active_token = ""

st.title("📄 PDF Auto-Splitter & Token System")

# ==========================================
# 🔐 BAGIAN 1: VERIFIKASI TOKEN WHATSAPP
# ==========================================
if not st.session_state.token_verified:
    st.subheader("🔐 Masukkan Token Akses")
    st.info("Dapatkan token akses melalui bot WhatsApp kami sebelum menggunakan aplikasi ini.")
    
    input_token = st.text_input("Masukkan Token Anda:", type="default")
    
    if st.button("Verifikasi Token"):
        token_upper = input_token.strip().upper()
        
        if token_upper in st.session_state.token_db:
            t_data = st.session_state.token_db[token_upper]
            
            # Cek apakah kuota habis
            if t_data["used_count"] >= t_data["max_uses"]:
                st.error(f"❌ Token sudah habis! Telah digunakan {t_data['used_count']}/{t_data['max_uses']} kali.")
            else:
                # Kurangi / catat penggunaan
                t_data["used_count"] += 1
                st.session_state.token_verified = True
                st.session_state.active_token = token_upper
                st.success("✅ Token valid! Memuat aplikasi...")
                st.rerun()
        else:
            st.error("❌ Token tidak ditemukan atau salah.")
            
    st.stop() # Menghentikan eksekusi kode di bawah jika belum verifikasi

# Jika sudah terverifikasi, tampilkan sisa kuota di sidebar
sisa_kuota = st.session_state.token_db[st.session_state.active_token]["max_uses"] - st.session_state.token_db[st.session_state.active_token]["used_count"]
st.sidebar.success(f"🔑 Token Aktif: **{st.session_state.active_token}**")
st.sidebar.info(f"📊 Sisa Kuota Sesi Ini: **{sisa_kuota}x pakai**")

if st.sidebar.button("Keluar / Ganti Token"):
    st.session_state.token_verified = False
    st.rerun()

# ==========================================
# 🚀 BAGIAN 2: APLIKASI UTAMA (PDF SPLITTER)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.subheader("📁 Template & Contoh File")
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

st.subheader("⚙️ Pengaturan Split")
opsi_halaman = st.radio(
    "Pilih jumlah halaman PDF untuk setiap 1 nama di Excel:",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: f"{x} Halaman",
    horizontal=True
)
pages_per_split = opsi_halaman

st.divider()

pdf_file = st.file_uploader("1. Upload PDF Sertifikat", type="pdf")
excel_file = st.file_uploader("2. Upload Excel Daftar Nama", type="xlsx")

if pdf_file and excel_file:
    df = pd.read_excel(excel_file)
    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
    
    if kolom_nama:
        nama_list = df[kolom_nama].tolist()
    else:
        nama_list = df.iloc[:, 0].tolist()
        st.warning("⚠️ Kolom 'Nama' tidak ditemukan, menggunakan kolom pertama sebagai gantinya.")
    
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    if st.button("🚀 Proses & Download Zip", use_container_width=True):
        with st.spinner("Sedang memproses file..."):
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
                        
                        nama_file = str(nama).strip().replace("/", "_").replace("\\", "_")
                        zip_file.writestr(f"{nama_file}.pdf", pdf_buffer.getvalue())
            
            st.success("✅ Selesai! Silakan unduh hasilnya di bawah ini.")
            st.download_button(
                label="📥 Download Semua Hasil (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="hasil_split.zip",
                mime="application/zip",
                use_container_width=True
            )
