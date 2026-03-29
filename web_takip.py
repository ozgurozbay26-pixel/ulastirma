import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# LÜTFEN: Kendi Google Sheets URL'ni buraya tırnak içine yapıştır
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # VERİ OKUMA (Hafızayı tazelemek için ttl=0)
    df = conn.read(spreadsheet=URL, ttl=0)

    # Tablo tamamen boşsa veya başlıklar yoksa hata vermemesi için:
    if df is None or df.empty:
        df = pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    else:
        # Sütun isimlerini garantiye alalım (Küçük harf)
        df.columns = [c.lower() for c in df.columns]

    # YAN PANEL FORM
    st.sidebar.header("📝 Yeni Kayıt Girişi")
    s_sofor = st.sidebar.selectbox("Şoför Seçin", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
    s_plaka = st.sidebar.selectbox("Plaka Seçin", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
    s_saat = st.sidebar.time_input("Saat", datetime.now().time())
    s_km = st.sidebar.text_input("Araç KM")
    s_gorev = st.sidebar.text_area("Görev Tanımı")

    if st.sidebar.button("KAYDEDİLSİN Mİ?", type="primary"):
        if s_sofor != "Seçiniz..." and s_gorev.strip():
            yeni_satir = pd.DataFrame([{
                "tarih": datetime.now().strftime("%d.%m.%Y"),
                "saat": s_saat.strftime("%H:%M"),
                "sofor": s_sofor,
                "plaka": s_plaka,
                "km": s_km,
                "gorev": s_gorev
            }])
            
            # Eski veriyle yeniyi birleştir
            son_df = pd.concat([df, yeni_satir], ignore_index=True)
            
            # Google Sheets'e gönder
            conn.update(spreadsheet=URL, data=son_df)
            st.sidebar.success("✅ Excel'e Başarıyla Yazıldı!")
            st.rerun()
        else:
            st.sidebar.error("Lütfen şoför ve görev kısımlarını doldurun.")

    # ANA EKRAN TABLO
    st.subheader("📋 Güncel Hareket Listesi")
    if not df.empty:
        st.dataframe(df.dropna(how='all'), use_container_width=True, hide_index=True)
    else:
        st.info("Kayıtlar listeleniyor veya henüz veri girilmemiş...")

except Exception as e:
    st.error("🚨 BAĞLANTI SORUNU!")
    st.write(f"Hata Detayı: {e}")
    st.info("EĞER BURADA 403 YAZIYORSA: Lütfen Google Sheets dosyasını 'ozgurozbay@banded-arch-465808-q9.iam.gserviceaccount.com' adresiyle 'Düzenleyen' olarak paylaş.")
