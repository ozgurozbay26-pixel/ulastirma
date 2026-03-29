import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- KENDİ GOOGLE SHEETS LİNKİNİ BURAYA YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

# Bağlantıyı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# --- VERİ OKUMA ---
def verileri_getir():
    try:
        # TTL=0 yaparak her saniye güncel veriyi çekmesini sağlıyoruz
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
        return df
    except:
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

df_mevcut = verileri_getir()

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat Seçimi", time(12, 00)) # İŞTE BURADA!
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        # Yeni satırı senin seçtiğin saatle oluşturuyoruz
        yeni_kayit = pd.DataFrame([{
            "tarih": s_tarih.strftime("%d.%m.%Y"),
            "saat": s_saat.strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # Mevcut veriyi al ve üstüne ekle
            guncel_df = verileri_getir()
            son_df = pd.concat([guncel_df, yeni_kayit], ignore_index=True)
            
            # Google Sheets'e gönder
            conn.update(spreadsheet=URL, data=son_df)
            st.sidebar.success("Kayıt Başarıyla Eklendi!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Hata: {e}")
    else:
        st.sidebar.error("Lütfen zorunlu alanları doldurun!")

# --- TABLO GÖRÜNTÜLEME ---
st.markdown("### 📋 Güncel Hareket Listesi")
if not df_mevcut.empty:
    # Tabloyu gösterirken boş satırları gizle
    df_goster = df_mevcut.dropna(how='all')
    st.dataframe(df_goster, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor.")
