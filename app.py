import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import os

st.set_page_config(page_title="PDF Splitter & Token Generator", page_icon="📄")

# --- SIMULASI DATABASE TOKEN (Di produksi, gunakan Database seperti SQLite/PostgreSQL) ---
if 'token_db' not in st.session_state:
    st.session_state.token_db = {
        # Format: "TOKEN": {"max_uses": jumlah, "used_count": jumlah}
        "DEMO2026": {"max_uses": 3, "used_count": 0}
    }

st.title("📄 PDF Auto-Splitter & Sistem Token")

# --- SIDEBAR: NAVIGASI & MENU ADMIN ---
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio("Pilih Menu:", ["Aplikasi Utama (Split PDF)", "Dapatkan Token (Upload PDF)", "🔑 Menu Khusus Admin"])

# ==========================================
# 1. MENU KHUSUS ADMIN (Buat Token)
# ==========================================
if menu == "🔑 Menu Khusus Admin":
    st.subheader("🛠️ Panel Admin - Pembuatan Token")
    st.info("Gunakan menu ini untuk menghasilkan token baru bagi pengguna.")
    
    with st.form("form_admin_token"):
        admin_password = st.text_input("Password Admin:", type="password")
        new_token_name = st.text_input("Nama/Kode Token (Contoh: TOKEN-USER-01):").upper()
        max_quota = st.number_input("Batas Maksimal Penggunaan:", min_value=1, max_value=100, value=5)
        
        submit_admin = st.form_submit_button("Buat Token Baru")
        
        if submit_admin:
            # Password sederhana untuk contoh (ubah sesuai kebutuhan)
            if admin_password == "admin123":
                if new_token_name:
                    if new_token_name in st.session_state.token_db:
                        st.warning("⚠️ Token tersebut sudah ada di database!")
                    else:
                        st.session_state.token_db[new_token_name] = {
                            "max_uses": max_quota,
                            "used_count": 0
                        }
                        st.success(f"✅ Token **{new_token_name}** berhasil dibuat dengan kuota {max_quota}x pakai!")
                else:
                    st.error("❌ Nama token tidak boleh kosong.")
            else:
                st.error("❌ Password admin salah!")

    st.divider()
    st.subheader("📊 Daftar Token Aktif Saat Ini")
    # Tampilkan daftar token dalam bentuk tabel
    if st.session_state.token_db:
        df_token = pd.DataFrame([
            {"Token": k, "Maks Kuota": v["max_uses"], "Terpakai": v["used_count"], "Sisa": v["max_uses"] - v["used_count"]}
            for k, v in st.session_state.token_db.items()
        ])
        st.dataframe(df_token, use_container_width=True)

# ==========================================
# 2. MENU DAPATKAN TOKEN (Cek PDF User)
# ==========================================
elif menu == "Dapatkan Token (Upload PDF)":
    st.subheader("🎯 Validasi PDF untuk Mendapatkan Token")
    st.write("Upload file PDF Anda ke sini. Sistem akan mengecek kebenaran/format file tersebut. Jika valid, token akan otomatis diberikan!")
    
    uploaded_check_pdf = st.file_uploader("Upload PDF untuk dicek:", type="pdf", key="check_pdf")
    
    if uploaded_check_pdf is not None:
        try:
            reader_check = PdfReader(uploaded_check_pdf)
            jumlah_halaman = len(reader_check.pages)
            
            # CONTOH ATURAN VALIDASI PDF (Sesuaikan kebutuhan, misal: minimal 1 halaman atau teks tertentu)
            pdf_valid = True 
            
            if jumlah_halaman < 1:
                pdf_valid = False
            
            if pdf_valid:
                st.success("✅ File PDF Berhasil Diverifikasi dan Benar!")
                
                # Generate token otomatis untuk user berdasarkan nama file atau acak
                generated_token = f"TKN-{uploaded_check_pdf.name[:5].upper()}-2026"
                
                # Masukkan ke database jika belum ada
                if generated_token not in st.session_state.token_db:
                    st.session_state.token_db[generated_token] = {"max_uses": 3, "used_count": 0}
                
                st.info(f"🎉 Selamat! Token WhatsApp Anda:\n### **{generated_token}**")
                st.markdown("*(Simpan token ini untuk digunakan pada menu **Aplikasi Utama** atau kirimkan via bot WhatsApp Anda)*")
            else:
                st.error("❌ Format PDF tidak sesuai persyaratan validasi.")
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat membaca PDF: {e}")

# ==========================================
# 3. APLIKASI UTAMA (Split PDF dengan Token)
# ==========================================
elif menu == "Aplikasi Utama (Split PDF)":
    st.subheader("🚀 PDF Auto-Splitter & Renamer")
    
    # Verifikasi Token sebelum pakai alat
    input_token = st.text_input("Masukkan Token Akses Anda:", type="default")
    
    if input_token:
        token_key = input_token.strip().upper()
        if token_key in st.session_state.token_db:
            t_data = st.session_state.token_db[token_key]
            
            if t_data["used_count"] >= t_data["max_uses"]:
                st.error(f"❌ Token sudah habis! Telah digunakan {t_data['used_count']}/{t_data['max_uses']} kali.")
            else:
                sisa = t_data["max_uses"] - t_data["used_count"]
                st.success(f"✅ Token Valid! Sisa kuota: {sisa} kali.")
                
                # Bagian File Upload & Proses Split
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                
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
                pdf_file = st.file_uploader("1. Upload PDF Sertifikat", type="pdf", key="split_pdf")
                excel_file = st.file_uploader("2. Upload Excel Daftar Nama", type="xlsx", key="split_excel")

                if pdf_file and excel_file:
                    df = pd.read_excel(excel_file)
                    kolom_nama = next((col for col in df.columns if col.lower() == 'nama'), None)
                    
                    if kolom_nama:
                        nama_list = df[kolom_nama].tolist()
                    else:
                        nama_list = df.iloc[:, 0].tolist()
                        st.warning("⚠️ Kolom 'Nama' tidak ditemukan, menggunakan kolom pertama.")
                    
                    reader = PdfReader(pdf_file)
                    total_pages = len(reader.pages)
                    
                    if st.button("🚀 Proses & Download Zip", use_container_width=True):
                        # Kurangi kuota token saat tombol proses ditekan
                        t_data["used_count"] += 1
                        
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
                            
                            st.success("✅ Selesai! Kuota token Anda telah dikurangi 1.")
                            st.download_button(
                                label="📥 Download Semua Hasil (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="hasil_split.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
        else:
            st.error("❌ Token tidak ditemukan. Silakan buat token melalui menu 'Dapatkan Token' atau hubungi admin.")
    else:
        st.info("ℹ️ Silakan masukkan token akses Anda untuk membuka menu split PDF.")
