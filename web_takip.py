import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Ulaştırma Takip", layout="wide")

# --- BURAYA KENDİ TABLO LİNKİNİ YAPIŞTIR ---
# Linkin sonundaki /edit... kısmını silmene gerek yok, direkt yapıştır.
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Takip")

try:
    # Bağlantıyı oluştur
    conn = st.connection("gsheets", type=GSheetsConnection)

    # VERİ OKUMA
    # ttl=0 ekliyoruz ki her zaman en güncel hali gelsin
    df = conn.read(spreadsheet=URL, ttl=0)
    
    # Eğer tablo tamamen boşsa başlıkları tanımla
    if df is None or df.empty:
        df = pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

    # YAN PANEL FORM
    st.sidebar.header("📝 Yeni Kayıt")
    s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
    s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
    s_km = st.sidebar.text_input("KM")
    s_gorev = st.sidebar.text_area("Görev")

    if st.sidebar.button("KAYDET"):
        if s_sofor != "Seçiniz..." and s_gorev:
            yeni = pd.DataFrame([{
                "tarih": datetime.now().strftime("%d.%m.%Y"),
                "saat": datetime.now().strftime("%H:%M"),
                "sofor": s_sofor,
                "plaka": s_plaka,
                "km": s_km,
                "gorev": s_gorev
            }])
            
            # Veriyi birleştir ve gönder
            guncel_df = pd.concat([df, yeni], ignore_index=True)
            conn.update(spreadsheet=URL, data=guncel_df)
            st.sidebar.success("Kayıt Başarılı!")
            st.rerun()
        else:
            st.sidebar.warning("Lütfen şoför ve görev girin.")

    # TABLOYU GÖSTER
    st.subheader("📋 Hareket Listesi")
    if not df.empty:
        # Boş satırları temizleyip göster
        st.dataframe(df.dropna(how='all'), use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kayıt yok veya veriler okunuyor...")

except Exception as e:
    st.error("🚨 SİSTEMDE BİR SORUN VAR!")
    st.write(f"Hata detayı: {e}")
    st.info("İpucu: Eğer '403' veya 'Permission' hatası varsa, Google Sheets paylaşım ayarını kontrol et.")
