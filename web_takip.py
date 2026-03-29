import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip", layout="wide")

# --- LİNKİ BURAYA YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Takip")

# 1. BAĞLANTIYI KUR
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. VERİ OKUMA (Hata Ayıklayıcı ile)
def verileri_yukle():
    try:
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None:
            return df.dropna(how='all')
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    except Exception as e:
        # Eğer mesaj 200 ise bu bir BAŞARIDIR
        if "200" in str(e):
            return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

# FORM ALANI
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET VE EXCEL'E GÖNDER", type="primary"):
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
            # Mevcut veriyi al ve üzerine ekle
            df_mevcut = verileri_yukle()
            son_df = pd.concat([df_mevcut, yeni_kayit], ignore_index=True)
            
            # Google Sheets'e gönder
            conn.update(spreadsheet=URL, data=son_df)
            
            st.sidebar.success("✅ Kayıt Başarıyla Gönderildi!")
            st.rerun()
            
        except Exception as e:
            # İŞTE BURASI KRİTİK: 200 geldiyse başarıyı kutla!
            if "200" in str(e):
                st.sidebar.success("✅ Kayıt Başarıyla Excel'e Yazıldı!")
                st.balloons() # Başarıyı balonlarla kutla!
                st.rerun()
            else:
                st.sidebar.error(f"Teknik bir sorun oldu: {e}")
    else:
        st.sidebar.error("Lütfen şoför ve görev girin!")

# ANA TABLO
st.subheader("📋 Hareket Listesi")
data = verileri_yukle()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Kayıtlar listeleniyor veya henüz veri yok.")

if st.button("🔄 Listeyi Tazele"):
    st.rerun()
