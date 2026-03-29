import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- 1. BAĞLANTI AYARLARI ---
@st.cache_resource
def gsheet_baglan():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    # Senin Excel Linkin
    url = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
    return client.open_by_url(url)

try:
    doc = gsheet_baglan()
    sheet_kayitlar = doc.get_worksheet(0) # Ana kayıt sayfası
    
    # ŞOFÖRLERİ EXCEL'DEN ÇEK
    try:
        sheet_sofor = doc.worksheet("soforler")
        sofor_listesi = sorted(sheet_sofor.col_values(1)[1:]) # Başlık hariç al ve alfabetik sırala
    except:
        sofor_listesi = ["Sayfa Bulunamadı!"]

    # ARAÇLARI EXCEL'DEN ÇEK
    try:
        sheet_arac = doc.worksheet("araclar")
        arac_listesi = sorted(sheet_arac.col_values(1)[1:]) # Başlık hariç al ve alfabetik sırala
    except:
        arac_listesi = ["Sayfa Bulunamadı!"]

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 2. YAN PANEL (YENİ KAYIT) ---
st.sidebar.header("📝 Yeni Hareket Girişi")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat Seçimi", time(12, 0))

# LİSTELER ARTIK EXCEL'DEN GELİYOR
s_sofor = st.sidebar.selectbox("Şoför Seçin", ["Seçiniz..."] + sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", ["Seçiniz..."] + arac_listesi)

s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("VERİTABANINA KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_plaka != "Seçiniz..." and s_gorev.strip():
        yeni_satir = [
            s_tarih.strftime("%d.%m.%Y"),
            s_saat.strftime("%H:%M"),
            s_sofor,
            s_plaka,
            s_km,
            s_gorev
        ]
        sheet_kayitlar.append_row(yeni_satir)
        st.sidebar.success("✅ Kayıt Arşive Eklendi!")
        st.cache_data.clear()
        st.rerun()
    else:
        st.sidebar.error("Lütfen tüm alanları doldurun.")

# --- 3. ANA EKRAN (ARŞİV VE FİLTRE) ---
st.title("🚗 Sözcü Ulaştırma Hareket Arşivi")

try:
    data = sheet_kayitlar.get_all_records()
    df = pd.DataFrame(data)
except:
    df = pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

if not df.empty:
    st.markdown("### 🔍 Detaylı Sorgulama")
    c1, c2, c3 = st.columns(3)
    with c1: f_sofor = st.multiselect("Şoföre Göre", options=df["sofor"].unique())
    with c2: f_plaka = st.multiselect("Plakaya Göre", options=df["plaka"].unique())
    with c3: f_tarih = st.multiselect("Tarihe Göre", options=df["tarih"].unique())

    f_df = df.copy()
    if f_sofor: f_df = f_df[f_df["sofor"].isin(f_sofor)]
    if f_plaka: f_df = f_df[f_df["plaka"].isin(f_plaka)]
    if f_tarih: f_df = f_df[f_df["tarih"].isin(f_tarih)]

    st.write(f"📊 Toplam {len(f_df)} kayıt bulundu.")
    st.dataframe(f_df, use_container_width=True, hide_index=True)
else:
    st.info("Sistem hazır, kayıt yapıldığında burada listelenecek.")

if st.button("🔄 Verileri ve Listeleri Yenile"):
    st.cache_data.clear()
    st.rerun()
