import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date

st.set_page_config(page_title="Sözcü Ulaştırma Takip", layout="wide")

# --- KRİTİK ADIM: Google Sheets Linkini Buraya Yapıştır ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"

# Bağlantı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Görev Takip")

# Yan Panel Form
st.sidebar.header("📝 Yeni Kayıt")
soforler = ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"]
plakalar = ["Seçiniz...", "34 ABC 123", "06 XYZ 789"]

s_sofor = st.sidebar.selectbox("Şoför", soforler)
s_plaka = st.sidebar.selectbox("Plaka", plakalar)
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev:
        yeni_satir = pd.DataFrame([{
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        # Mevcut veriyi bu URL üzerinden çek
        try:
            df = conn.read(spreadsheet=SPREADSHEET_URL)
            updated_df = pd.concat([df, yeni_satir], ignore_index=True)
            # URL üzerinden güncelle
            conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
        except:
            # Tablo boşsa sıfırdan oluştur
            conn.update(spreadsheet=SPREADSHEET_URL, data=yeni_satir)
            
        st.sidebar.success("Excel'e başarıyla kaydedildi!")
        st.rerun()

# Listeyi Göster
try:
    data = conn.read(spreadsheet=SPREADSHEET_URL)
    st.subheader("📋 Güncel Hareket Listesi")
    st.dataframe(data, use_container_width=True, hide_index=True)
except:
    st.info("Henüz kayıt bulunmuyor.")
