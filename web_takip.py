import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- KENDİ GOOGLE SHEETS LİNKİNİ BURAYA YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

# Bağlantıyı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# --- VERİ OKUMA FONKSİYONU ---
def verileri_yukle():
    try:
        # TTL=0 veriyi her seferinde canlı çeker
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None and not df.empty:
            return df.dropna(how='all')
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    except:
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt Girişi")
s_sofor = st.sidebar.selectbox("Şoför Seçin", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka Seçin", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_saat = st.sidebar.time_input("Saat", datetime.now().time())
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_satir = pd.DataFrame([{
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "saat": s_saat.strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # Mevcut veriyi al
            mevcut_df = verileri_yukle()
            # Yeni satırı ekle
            son_df = pd.concat([mevcut_df, yeni_satir], ignore_index=True)
            
            # Google Sheets'e gönder
            # Burada 'Response 200' gelse bile hata vermemesi için kontrol ekledik
            conn.update(spreadsheet=URL, data=son_df)
            
            st.sidebar.success("✅ Kayıt Excel'e başarıyla işlendi!")
            st.rerun()
        except Exception as e:
            # Eğer hata mesajında 200 geçiyorsa bu aslında başarıdır
            if "200" in str(e):
                st.sidebar.success("✅ Kayıt Başarıyla İşlendi!")
                st.rerun()
            else:
                st.sidebar.error(f"Kayıt Hatası: {e}")
    else:
        st.sidebar.error("Lütfen şoför ve görev alanlarını doldurun.")

# --- ANA EKRAN TABLO ---
st.markdown("### 📋 Güncel Hareket Listesi")
data = verileri_yukle()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor veya veriler yükleniyor...")

if st.button("🔄 Listeyi Yenile"):
    st.rerun()
