import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sözcü Takip | Özgür Özbay", layout="wide", page_icon="🚗")

# --- RESİM LİNKİ (SİZİN GÖNDERDİĞİNİZ) ---
LOGO_URL = "https://i.ibb.co/gZLkm4KF/channels4-profile.jpg"

# --- 0. LOGIN SİSTEMİ ---
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            # Giriş ekranında logonuz
            st.image(LOGO_URL, width=150)
            st.title("Sistem Girişi")
            user = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            
            if st.button("Giriş Yap", use_container_width=True):
                # Kullanıcı: ozgur | Şifre: sozcu2024
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
                temp_sheet = doc.worksheet(sayfa_adi)
                return sorted(temp_sheet.col_values(1)[1:])
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
        st.error("⚠️ Excel formatı hatalı! A1 hücresine 'id' yazmayı unutmayın.")
        st.stop()

    # --- 3. ÜST PANEL (YENİ LOGO VE BAŞLIK) ---
    col_logo, col_title, col_admin = st.columns([0.8, 4, 1.5])
    
    with col_logo:
        # Ana sayfada logonuz
        st.image(LOGO_URL, width=80)

    with col_title:
        st.markdown("<h1 style='margin-top: 5px;'>Ulaştırma Hareket Takip Arşivi</h1>", unsafe_allow_html=True)

    with col_admin:
        st.markdown(f"""
            <div style="background-color:#f8f9fa; padding:10px; border-radius:8px; border:1px solid #dee2e6; text-align:center;">
                <b style="color:#212529; font-size:15px;">Özgür Özbay</b><br>
                <span style="font-size:12px; color:#6c757d;">Sistem Yöneticisi</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # --- 4. YAN PANEL (KAYIT) ---
    st.sidebar.header("📝 Yeni Kayıt")
    with st.sidebar.form("yeni_form", clear_on_submit=True):
        s_tarih = st.date_input("Tarih", datetime.now())
        s_saat = st.time_input("Saat", time(12, 0))
        s_sofor = st.selectbox("Şoför", ["Seçiniz..."] + sofor_listesi)
        s_plaka = st.selectbox("Plaka", ["Seçiniz..."] + arac_listesi)
        s_km = st.text_input("Araç KM")
        s_durum = st.selectbox("Durum", ["Seçiniz..."] + durum_listesi)
        s_gorev = st.text_area("Görev Tanımı")
        submit = st.form_submit_button("SİSTEME İŞLE")

    if submit:
        if s_sofor != "Seçiniz..." and s_plaka != "Seçiniz...":
            yeni_id = str(uuid.uuid4())[:8]
            yeni_satir = [yeni_id, s_tarih.strftime("%d.%m.%Y"), s_saat.strftime("%H:%M"), s_sofor, s_plaka, s_km, s_gorev, s_durum]
            sheet_kayitlar.append_row(yeni_satir)
            st.sidebar.success("✅ Kayıt Tamamlandı!")
            st.cache_data.clear()
            st.rerun()

    # --- 5. ANA EKRAN (ARŞİV) ---
    if not df.empty and "id" in df.columns:
        st.markdown("### 🔍 Arşiv Sorgulama")
        c1, c2, c3, c4 = st.columns(4)
        with c1: f_sofor = st.multiselect("Şoför", df["sofor"].unique())
        with c2: f_plaka = st.multiselect("Plaka", df["plaka"].unique())
        with c3: f_tarih = st.multiselect("Tarih", df["tarih"].unique())
        with c4: f_durum = st.multiselect("Durum", df["durum"].unique())

        f_df = df.copy()
        if f_sofor: f_df = f_df[f_df["sofor"].isin(f_sofor)]
        if f_plaka: f_df = f_df[f_df["plaka"].isin(f_plaka)]
        if f_tarih: f_df = f_df[f_df["tarih"].isin(f_tarih)]
        if f_durum: f_df = f_df[f_df["durum"].isin(f_durum)]

        st.dataframe(f_df, use_container_width=True, hide_index=True)

        # --- SİLME / DÜZENLEME ---
        st.markdown("---")
        with st.expander("🛠️ Kayıt Düzenleme ve Silme Paneli"):
            secilen_id = st.selectbox("İşlem için ID seçin:", ["Seçiniz..."] + f_df["id"].tolist())
            if secilen_id != "Seçiniz...":
                idx_list = df[df['id'] == secilen_id].index
                if not idx_list.empty:
                    kayit_index = idx_list[0] + 2
                    eski_veri = df[df['id'] == secilen_id].iloc[0]
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        yeni_km = st.text_input("KM Güncelle", value=str(eski_veri.get('km', '')))
                        yeni_gorev = st.text_area("Görev Güncelle", value=str(eski_veri.get('gorev', '')))
                        if st.button("KAYDI GÜNCELLE"):
                            sheet_kayitlar.update_cell(kayit_index, 6, yeni_km)
                            sheet_kayitlar.update_cell(kayit_index, 7, yeni_gorev)
                            st.success("Güncellendi!")
                            st.cache_data.clear()
                            st.rerun()
                    with col_del:
                        st.warning("⚠️ Silme geri alınamaz!")
                        if st.button("🗑️ KAYDI SİL"):
                            sheet_kayitlar.delete_rows(int(kayit_index))
                            st.success("Silindi!")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Kayıtlar listeleniyor...")

    st.markdown(f"<div style='text-align: center; color: grey; font-size: 10px; margin-top: 50px;'>© {datetime.now().year} Sözcü Ulaştırma | Özgür Özbay</div>", unsafe_allow_html=True)
