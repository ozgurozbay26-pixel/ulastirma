import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# Google Sheets Linkin
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

# Bağlantıyı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# --- VERİ OKUMA ---
def verileri_getir():
    try:
        # TTL=0 veriyi her seferinde canlı çeker
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None:
            return df.dropna(how='all') # Boş satırları temizle
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    except:
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat Seçimi", time(12, 00))
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_kayit = pd.DataFrame([{
            "tarih": s_tarih.strftime("%d.%m.%Y"),
            "saat": s_saat.strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # Mevcut veriyi al ve yeni satırı ekle
            df_mevcut = verileri_getir()
            son_df = pd.concat([df_mevcut, yeni_kayit], ignore_index=True)
            
            # Google Sheets'e gönder (200 sonucunu ekrana basma!)
            conn.update(spreadsheet=URL, data=son_df)
            
            st.sidebar.success("✅ Kayıt Excel'e başarıyla işlendi!")
            st.rerun() # Sayfayı yenileyerek tabloyu güncelle
        except Exception as e:
            st.sidebar.error(f"Kayıt yapılamadı: {e}")
    else:
        st.sidebar.error("Lütfen şoför ve görev kısımlarını doldurun!")

# --- ANA EKRAN TABLO ---
st.markdown("### 📋 Güncel Hareket Listesi")
data = verileri_getir()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor veya veriler yükleniyor...")

# Sayfayı el ile yenileme
if st.button("🔄 Listeyi Tazele"):
    st.rerun()
