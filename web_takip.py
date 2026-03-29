import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- BURAYA GOOGLE SHEETS LİNKİNİ YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# Bağlantıyı kur
conn = st.connection("gsheets", type=GSheetsConnection)

# VERİ OKUMA FONKSİYONU
def verileri_getir():
    try:
        # ttl=0 ile her zaman en son halini çekiyoruz
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None and not df.empty:
            return df.dropna(how='all')
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    except Exception as e:
        # Eğer okurken 200 gelirse aslında başarılıdır
        if "200" in str(e):
            st.info("Veriler tazeleniyor...")
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

# YAN PANEL FORM
st.sidebar.header("📝 Yeni Kayıt")
soforler = ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"]
plakalar = ["Seçiniz...", "34 ABC 123", "06 XYZ 789"]

s_sofor = st.sidebar.selectbox("Şoför", soforler)
s_plaka = st.sidebar.selectbox("Plaka", plakalar)
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET VE GÖNDER", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_veri = pd.DataFrame([{
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "saat": datetime.now().strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # Mevcut veriyi al ve üzerine ekle
            df_eski = verileri_getir()
            df_yeni = pd.concat([df_eski, yeni_veri], ignore_index=True)
            
            # Google Sheets'e gönder
            conn.update(spreadsheet=URL, data=df_yeni)
            
            st.sidebar.success("✅ Kayıt Başarıyla Excel'e Yazıldı!")
            st.rerun()
            
        except Exception as e:
            # 200 mesajı gelirse bu bir BAŞARIDIR, hata değil!
            if "200" in str(e):
                st.sidebar.success("✅ Kayıt Başarıyla Tamamlandı!")
                st.rerun()
            else:
                st.sidebar.error(f"Bağlantı Kesildi: {e}")
    else:
        st.sidebar.warning("Lütfen boş alan bırakmayın.")

# ANA EKRAN TABLO
st.subheader("📋 Hareket Listesi")
data = verileri_getir()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor veya Google bağlantısı bekleniyor...")

if st.button("🔄 Verileri Güncelle"):
    st.rerun()
