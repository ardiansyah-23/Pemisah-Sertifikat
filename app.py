import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io

st.title("PDF Splitter Tool")
uploaded_file = st.file_uploader("Upload file PDF Anda", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    st.write(f"Total halaman: {len(reader.pages)}")
    
    page_num = st.number_input("Pilih nomor halaman untuk diambil", min_value=1, max_value=len(reader.pages))
    
    if st.button("Proses & Download"):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num-1])
        
        output = io.BytesIO()
        writer.write(output)
        
        st.download_button(
            label="Download PDF Hasil",
            data=output.getvalue(),
            file_name="hasil_split.pdf",
            mime="application/pdf"
        )
