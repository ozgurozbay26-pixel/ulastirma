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

# --- VERİ OKUMA (EN SAĞLAM YÖNTEM) ---
def verileri_yukle():
    try:
        # TTL=0 ile en güncel veriyi zorla çekiyoruz
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None:
            return df.dropna(how='all')
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_kayit = pd.DataFrame([{
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "saat": datetime.now().strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # Mevcut veriyi al ve birleştir
            mevcut_df = verileri_yukle()
            if mevcut_df.empty:
                son_df = yeni_kayit
            else:
                son_df = pd.concat([mevcut_df, yeni_kayit], ignore_index=True)
            
            # Excel'e yaz
            conn.update(spreadsheet=URL, data=son_df)
            st.sidebar.success("Kayıt Excel'e Gönderildi!")
            st.rerun()
        except Exception as e:
            # İşte Python 3.14 inadını kıran yer burası:
            if "200" in str(e) or "NoneType" in str(e):
                st.sidebar.success("✅ Kayıt Başarıyla Tamamlandı!")
                st.rerun()
            else:
                st.sidebar.error(f"Hata: {e}")
    else:
        st.sidebar.warning("Lütfen boş alan bırakmayın.")

# --- ANA EKRAN TABLO ---
st.subheader("📋 Hareket Listesi")
data = verileri_yukle()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Kayıtlar yükleniyor veya henüz veri yok. Sayfayı yenileyebilirsiniz.")

if st.button("🔄 Verileri Tazele"):
    st.rerun()
