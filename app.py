# ==================================
# ANALISIS & MENCEGAH BOROS API
# ==================================

# 1. MEMBUAT "INGATAN" APLIKASI
# Agar hasil tidak hilang saat layar ter-refresh, kita simpan di session_state
if "hasil_gizi" not in st.session_state:
    st.session_state.hasil_gizi = None

if image_file:
    image = Image.open(image_file)
    # 2. MENGECILKAN UKURAN GAMBAR
    # Mengompres gambar menjadi maksimal 800x800 piksel agar API tidak berat dan cepat merespons
    image.thumbnail((800, 800))

st.markdown("<br>", unsafe_allow_html=True)

analyze = st.button("🔍 Analisis Nutrisi")

if analyze:
    with st.spinner("🤖 AI sedang menerawang makanan ini..."):
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
            # 3. MENGGUNAKAN NAMA MODEL YANG BENAR
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image]
            )

            result_text = response.text
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(result_text)

            # 4. MENYIMPAN HASIL KE DALAM INGATAN
            st.session_state.hasil_gizi = data
            st.success("Analisis berhasil!")

        except Exception as e:
            error_text = str(e)
            if "429" in error_text:
                st.warning("⚠️ Kuota Gemini sedang istirahat. Silakan tunggu 1 menit lalu coba lagi.")
            else:
                st.error(f"Gagal menganalisis gambar: {e}")

# ==================================
# TAMPILAN HASIL (MEMBACA DARI INGATAN)
# ==================================

# Jika ada data di dalam ingatan, tampilkan hasilnya
if st.session_state.hasil_gizi:
    data = st.session_state.hasil_gizi

    st.markdown(
        f"""
        <div class="card">
            <h2>🍽️ {data['nama_makanan']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🔥 Kalori", f"{data['kalori_kcal']} kcal")
    with col2:
        st.metric("💪 Protein", f"{data['protein_g']} g")
    with col3:
        st.metric("🍚 Karbohidrat", f"{data['karbohidrat_g']} g")
    with col4:
        st.metric("🥑 Lemak", f"{data['lemak_g']} g")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
            <h3>💡 Tips Kesehatan</h3>
            <p>{data['tips']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
