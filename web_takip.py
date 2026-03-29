import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sözcü Takip | Özgür Özbay", layout="wide", page_icon="🚗")

# --- 0. LOGIN SİSTEMİ ---
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Ekranın ortasına şık bir giriş kutusu
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.image("https://www.sozcu.com.tr/static/img/sozcu-logo.png", width=200) # Opsiyonel Logo
            st.title("Sistem Girişi")
            user = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            
            # BURADAN ŞİFREYİ DEĞİŞTİREBİLİRSİN
            if st.button("Giriş Yap"):
                if user == "Yeliz" and password == "12345":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")
        return False
    return True

if login():
    # --- 1. BAĞLANTI ---
    @st.cache_resource
    def gsheet_baglan():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        url = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
        return client.open_by_url(url)

    try:
        doc = gsheet_baglan()
        sheet_kayitlar = doc.get_worksheet(0)
        
        def liste_getir(sayfa_adi):
            try:
                return sorted(doc.worksheet(sayfa_adi).col_values(1)[1:])
            except: return []

        sofor_listesi = liste_getir("soforler")
        arac_listesi = liste_getir("araclar")
        durum_listesi = liste_getir("durum")
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}"); st.stop()

    # --- 2. VERİ YÜKLEME ---
    try:
        rows = sheet_kayitlar.get_all_records()
        df = pd.DataFrame(rows)
    except Exception as e:
        st.error("⚠️ Excel formatı hatalı! A1 hücresine 'id' başlığını ekleyin.")
        st.stop()

    # --- 3. ÜST BİLGİ VE YÖNETİCİ İMZASI ---
    col_logo, col_admin = st.columns([4, 1])
    with col_logo:
        st.title("🚗 Sözcü Ulaştırma Hareket Takip")
    with col_admin:
        st.markdown(f"""
            <div style="background-color:#f0f2f6; padding:10px; border-radius:10px; border:1px solid #d1d5db; text-align:center;">
                <p style="margin:0; font-size:12px; color:#6b7280;">Sistem Yöneticisi</p>
                <b style="font-size:16px; color:#1f2937;">Özgür Özbay</b><br>
                <a href="/" style="text-decoration:none; font-size:10px; color:red;">Güvenli Çıkış</a>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # --- 4. YAN PANEL (YENİ KAYIT) ---
    st.sidebar.header("📝 Yeni Hareket")
    with st.sidebar.form("yeni_kayit_form", clear_on_submit=True):
        s_tarih = st.date_input("Tarih", datetime.now())
        s_saat = st.time_input("Saat", time(12, 0))
        s_sofor = st.selectbox("Şoför", ["Seçiniz..."] + sofor_listesi)
        s_plaka = st.selectbox("Plaka", ["Seçiniz..."] + arac_listesi)
        s_km = st.text_input("KM")
        s_durum = st.selectbox("Durum", ["Seçiniz..."] + durum_listesi)
        s_gorev = st.text_area("Görev")
        submit = st.form_submit_button("KAYDET")

    if submit:
        if s_sofor != "Seçiniz..." and s_plaka != "Seçiniz...":
            yeni_id = str(uuid.uuid4())[:8]
            yeni_satir = [yeni_id, s_tarih.strftime("%d.%m.%Y"), s_saat.strftime("%H:%M"), s_sofor, s_plaka, s_km, s_gorev, s_durum]
            sheet_kayitlar.append_row(yeni_satir)
            st.sidebar.success("Kayıt Eklendi!")
            st.cache_data.clear()
            st.rerun()

    # --- 5. ANA EKRAN & FİLTRELER ---
    if not df.empty and "id" in df.columns:
        st.markdown("### 🔍 Filtreleme ve Yönetim")
        c1, c2, c3, c4 = st.columns(4)
        with c1: f_sofor = st.multiselect("Şoför", df["sofor"].unique() if "sofor" in df else [])
        with c2: f_plaka = st.multiselect("Plaka", df["plaka"].unique() if "plaka" in df else [])
        with c3: f_tarih = st.multiselect("Tarih", df["tarih"].unique() if "tarih" in df else [])
        with c4: f_durum = st.multiselect("Durum", df["durum"].unique() if "durum" in df else [])

        f_df = df.copy()
        if f_sofor: f_df = f_df[f_df["sofor"].isin(f_sofor)]
        if f_plaka: f_df = f_df[f_df["plaka"].isin(f_plaka)]
        if f_tarih: f_df = f_df[f_df["tarih"].isin(f_tarih)]
        if f_durum: f_df = f_df[f_df["durum"].isin(f_durum)]

        st.dataframe(f_df, use_container_width=True, hide_index=True)

        # --- SİLME VE DÜZENLEME ---
        st.markdown("---")
        st.subheader("🛠️ Kayıt Düzenle veya Sil")
        
        secilen_id = st.selectbox("İşlem yapılacak kaydın ID'sini seçin:", ["Seçiniz..."] + f_df["id"].tolist())
        
        if secilen_id != "Seçiniz...":
            idx_list = df[df['id'] == secilen_id].index
            if not idx_list.empty:
                kayit_index = idx_list[0] + 2
                eski_veri = df[df['id'] == secilen_id].iloc[0]

                col_edit, col_del = st.columns(2)
                with col_edit:
                    yeni_km = st.text_input("Yeni KM", value=str(eski_veri.get('km', '')))
                    yeni_gorev = st.text_area("Yeni Görev", value=str(eski_veri.get('gorev', '')))
                    if st.button("BİLGİLERİ GÜNCELLE"):
                        sheet_kayitlar.update_cell(kayit_index, 6, yeni_km)
                        sheet_kayitlar.update_cell(kayit_index, 7, yeni_gorev)
                        st.success("Güncellendi!")
                        st.cache_data.clear()
                        st.rerun()

                with col_del:
                    st.warning("⚠️ Bu kayıt kalıcı olarak silinecek!")
                    if st.button("SEÇİLİ KAYDI SİL"):
                        sheet_kayitlar.delete_rows(int(kayit_index))
                        st.success("Kayıt Silindi!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.warning("Henüz kayıt bulunmuyor.")
