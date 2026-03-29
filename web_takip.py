import streamlit as st
import pandas as pd
from datetime import date
# Google Sheets için gerekli kütüphane
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sözcü Takip (GSheets)", layout="wide")

# --- 1. BAĞLANTI ---
# Google Sheets URL'ni buraya yapıştır
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. SABİT LİSTELER (Veritabanı derdi yok!) ---
soforler = ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"]
plakalar = ["Seçiniz...", "34 ABC 123", "06 XYZ 789", "35 KML 456"]

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# --- 3. KAYIT FORMU ---
st.sidebar.header("📝 Yeni Kayıt Girişi")
s_sofor = st.sidebar.selectbox("Şoför", soforler)
s_plaka = st.sidebar.selectbox("Plaka", plakalar)
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("VERİYİ EXCEL'E KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev:
        yeni_satir = pd.DataFrame([{
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "saat": "---",
            "km": s_km,
            "gorev": s_gorev
        }])
        
        # Mevcut veriyi çek ve yeni satırı ekle
        existing_data = conn.read(spreadsheet=GSHEET_URL)
        updated_df = pd.concat([existing_data, yeni_satir], ignore_index=True)
        conn.update(spreadsheet=GSHEET_URL, data=updated_df)
        
        st.sidebar.success("Kayıt Excel'e işlendi!")
        st.rerun()

# --- 4. VERİLERİ GÖSTER ---
st.subheader("📋 Güncel Kayıtlar (Google Sheets'ten Canlı)")
try:
    df = conn.read(spreadsheet=GSHEET_URL)
    st.dataframe(df, use_container_width=True)
except:
    st.info("Henüz kayıt bulunamadı veya bağlantı bekleniyor.")
