import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- BURAYA KENDİ GOOGLE SHEETS LİNKİNİ YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

# Bağlantıyı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# --- VERİ OKUMA FONKSİYONU ---
def verileri_getir():
    try:
        # Veriyi çek, eğer boşsa veya hata verirse boş bir tablo oluştur
        df = conn.read(spreadsheet=URL, ttl="10s")
        if df is None or df.empty:
            return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
        return df
    except:
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

df_mevcut = verileri_getir()

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        # Yeni satır (Excel'deki sütunlarla birebir aynı sırada)
        yeni_kayit = pd.DataFrame([{
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "saat": datetime.now().strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        # Mevcut verinin altına ekle ve Excel'i güncelle
        try:
            # Önce güncel hali çek
            guncel_df = verileri_getir()
            # Yeni veriyi ekle
            son_df = pd.concat([guncel_df, yeni_kayit], ignore_index=True)
            # Excel'e yaz
            conn.update(spreadsheet=URL, data=son_df)
            st.sidebar.success("Kayıt Excel'e işlendi!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Hata oluştu: {e}")
    else:
        st.sidebar.error("Lütfen alanları doldurun!")

# --- TABLO GÖRÜNTÜLEME ---
st.markdown("### 📋 Güncel Hareket Listesi")
if not df_mevcut.empty:
    # Tabloyu göster
    st.dataframe(df_mevcut, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor. İlk kaydı sol taraftan ekleyebilirsiniz.")

# Sayfayı el ile yenileme butonu
if st.button("Listeyi Güncelle"):
    st.rerun()
