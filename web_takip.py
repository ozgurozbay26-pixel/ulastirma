import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time

st.set_page_config(page_title="Sözcü Takip Paneli", layout="wide")

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
    # Senin paylaştığın link
    url = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
    return client.open_by_url(url).sheet1

try:
    sheet = gsheet_baglan()
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 2. VERİ GİRİŞ ALANI (SOL PANEL) ---
st.sidebar.header("📝 Yeni Kayıt Ekle")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat Seçimi", time(12, 0)) # İSTEDİĞİN SAAT SEÇİMİ
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("VERİTABANINA KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_satir = [
            s_tarih.strftime("%d.%m.%Y"),
            s_saat.strftime("%H:%M"),
            s_sofor,
            s_plaka,
            s_km,
            s_gorev
        ]
        sheet.append_row(yeni_satir)
        st.sidebar.success("✅ Kayıt Arşive Eklendi!")
        st.cache_data.clear() # Filtreleme için veriyi tazele
        st.rerun()
    else:
        st.sidebar.error("Lütfen Şoför ve Görev alanlarını doldurun.")

# --- 3. FİLTRELEME VE TABLO ALANI ---
st.title("🚗 Sözcü Ulaştırma Hareket Arşivi")

# Veriyi Excel'den Çek
try:
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
except:
    df = pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

if not df.empty:
    st.markdown("### 🔍 Arşivde Filtreleme Yap")
    
    # Filtreleme Seçenekleri (Yan yana 3 sütun)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        f_sofor = st.multiselect("Şoför Filtresi", options=df["sofor"].unique())
    with col2:
        f_plaka = st.multiselect("Plaka Filtresi", options=df["plaka"].unique())
    with col3:
        f_tarih = st.multiselect("Tarih Filtresi", options=df["tarih"].unique())

    # Filtreleri Uygula
    filtered_df = df.copy()
    if f_sofor:
        filtered_df = filtered_df[filtered_df["sofor"].isin(f_sofor)]
    if f_plaka:
        filtered_df = filtered_df[filtered_df["plaka"].isin(f_plaka)]
    if f_tarih:
        filtered_df = filtered_df[filtered_df["tarih"].isin(f_tarih)]

    # Tabloyu Göster
    st.write(f"📊 Toplam {len(filtered_df)} kayıt listeleniyor.")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Excel İndirme Butonu (Her ihtimale karşı)
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Seçili Kayıtları İndir (CSV)", data=csv, file_name="sozcu_arsiv.csv", mime="text/csv")

else:
    st.info("Henüz veritabanında kayıtlı veri bulunmuyor.")

if st.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()
