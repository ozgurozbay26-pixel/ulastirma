import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date

st.set_page_config(page_title="Sözcü Ulaştırma Takip", layout="wide")

# Google Sheets Bağlantısı (Secrets'tan otomatik okur)
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
        
        # Mevcut veriyi çek ve üstüne ekle
        df = conn.read()
        updated_df = pd.concat([df, yeni_satir], ignore_index=True)
        
        # Google Sheets'e gönder
        conn.update(data=updated_df)
        st.sidebar.success("Excel'e başarıyla kaydedildi!")
        st.rerun()

# Listeyi Göster
try:
    data = conn.read()
    st.subheader("📋 Güncel Hareket Listesi")
    st.dataframe(data, use_container_width=True, hide_index=True)
except:
    st.info("Henüz kayıt bulunmuyor.")
