import json
import streamlit as st
from PIL import Image
from google import genai

# ==================================
# PAGE CONFIG
# ==================================
st.set_page_config(
    page_title="CekGizi AI",
    page_icon="🥗",
    layout="wide"
)

# ==================================
# CUSTOM CSS
# ==================================
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(135deg, #f0fdf4, #ecfeff);
}
/* Hero Section */
.hero {
    background: linear-gradient(90deg, #10b981, #22c55e);
    padding: 30px;
    border-radius: 25px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
}
/* Cards */
.card {
    background: white;
    color: #111827 !important;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
/* Metrics */
[data-testid="metric-container"] {
    background: white !important;
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
}
[data-testid="metric-container"] label {
    color: #374151 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    color: #10b981 !important;
}
/* Button */
.stButton > button {
    width: 100%;
    height: 55px;
    border-radius: 15px;
    border: none;
    background: #10b981;
    color: white;
    font-size: 18px;
    font-weight: bold;
}
.stButton > button:hover {
    background: #059669;
    color: white;
}
/* Upload */
[data-testid="stFileUploader"] {
    background: white;
    border-radius: 15px;
    padding: 10px;
}
.stSuccess {
    border-radius: 15px;
}
/* Paksa warna metric */
[data-testid="metric-container"] * {
    color: #111827 !important;
}
[data-testid="stMetricLabel"] {
    color: #374151 !important;
}
/* Semua teks Streamlit */
label, p, span, small, div {
    color: #111827 !important;
}
/* Label kamera & uploader */
[data-testid="stCameraInput"] label, [data-testid="stFileUploader"] label {
    color: #111827 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"] {
    color: #111827 !important;
    font-weight: 600 !important;
}
[data-testid="stAlert"], [data-testid="stFileUploader"] *, [data-testid="stCameraInput"] * {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# HEADER & DESKRIPSI
# ==================================
st.markdown("""
<div class="hero">
    <h1>🥗 CekGizi AI</h1>
    <p style="font-size:18px;">Deteksi Kalori & Nutrisi Makanan dengan AI</p>
</div>
<div class="card">
    <h3>✨ Cara Menggunakan</h3>
    1️⃣ Upload foto makanan atau gunakan kamera<br>
    2️⃣ Klik tombol Analisis Nutrisi<br>
    3️⃣ AI akan memperkirakan: Nama makanan, Kalori, Protein, Karbohidrat, Lemak, dan Tips kesehatan.
</div>
""", unsafe_allow_html=True)

# ==================================
# API KEY & INISIALISASI
# ==================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ GEMINI_API_KEY tidak ditemukan di Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# ==================================
# INGATAN APLIKASI (MENCEGAH BOROS API)
# ==================================
if "hasil_gizi" not in st.session_state:
    st.session_state.hasil_gizi = None

# ==================================
# INPUT FOTO & PREVIEW
# ==================================
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("""
    <div class="card">
        <h3>📷 Upload Foto Makanan</h3>
        Gunakan kamera atau unggah dari galeri.
    </div>
    """, unsafe_allow_html=True)
    
    camera_image = st.camera_input("Ambil Foto")
    uploaded_file = st.file_uploader("Atau Upload Foto", type=["jpg", "jpeg", "png"])

image_file = camera_image if camera_image else uploaded_file

with right_col:
    st.markdown("""
    <div class="card">
        <h3>🖼️ Preview Gambar</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if image_file:
        preview_image = Image.open(image_file)
        st.image(preview_image, use_container_width=True)
    else:
        st.info("Upload foto makanan untuk melihat preview.")

# ==================================
# ANALISIS
# ==================================
st.markdown("<br>", unsafe_allow_html=True)

if image_file:
    analyze = st.button("🔍 Analisis Nutrisi")
    
    if analyze:
        with st.spinner("🤖 AI sedang menganalisis makanan..."):
            
            # Kompresi gambar agar hemat kuota
            proses_image = Image.open(image_file)
            proses_image.thumbnail((800, 800))
            
            prompt = """
            Anda adalah ahli gizi profesional.
            Lihat gambar makanan yang diberikan.
            Balas HANYA dalam format JSON berikut:
            {
            "nama_makanan":"",
            "kalori_kcal":"",
            "protein_g":"",
            "karbohidrat_g":"",
            "lemak_g":"",
            "tips":""
            }
            Jangan gunakan markdown. Jangan gunakan penjelasan tambahan.
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, proses_image]
                )
                
                result_text = response.text
                result_text = result_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(result_text)
                
                # Simpan ke ingatan
                st.session_state.hasil_gizi = data
                st.success("Analisis berhasil!")
                
            except Exception as e:
                error_text = str(e)
                if "429" in error_text:
                    st.warning("⚠️ Kuota Gemini sedang habis. Silakan tunggu beberapa saat.")
                else:
                    st.error(f"Gagal menganalisis gambar: {e}")

# ==================================
# TAMPILAN HASIL
# ==================================
if st.session_state.hasil_gizi:
    data = st.session_state.hasil_gizi
    
    st.markdown(
        f"""
        <div class="card">
            <h2>🍽️ {data.get('nama_makanan', 'Tidak diketahui')}</h2>
        </div>
        """, unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔥 Kalori", f"{data.get('kalori_kcal', 0)} kcal")
    with col2:
        st.metric("💪 Protein", f"{data.get('protein_g', 0)} g")
    with col3:
        st.metric("🍚 Karbo", f"{data.get('karbohidrat_g', 0)} g")
    with col4:
        st.metric("🥑 Lemak", f"{data.get('lemak_g', 0)} g")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card">
            <h3>💡 Tips Kesehatan</h3>
            <p>{data.get('tips', '-')}</p>
        </div>
        """, unsafe_allow_html=True
    )

# ==================================
# FOOTER
# ==================================
st.markdown("""
<br><br>
<center>
    <p style="color:gray;">CekGizi AI • Powered by Gemini AI</p>
</center>
""", unsafe_allow_html=True)
