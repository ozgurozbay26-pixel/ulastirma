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
        # TTL=0 yaparak verinin her saniye güncel gelmesini sağlıyoruz
        df = conn.read(spreadsheet=URL, ttl=0)
        if df is not None:
            return df.dropna(how='all') # Boş satırları temizle
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
    except:
        return pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])

# --- YAN PANEL FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat", time(12, 0))
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("LİSTEYE KAYDET", type="primary"):
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
            
            # Google Sheets'e gönder
            conn.update(spreadsheet=URL, data=son_df)
            
            # 200 mesajını görmezden gel, başarıyı kutla!
            st.sidebar.success("✅ Kayıt Excel'e Başarıyla İşlendi!")
            st.rerun() # Tabloyu anında güncellemek için sayfayı yenile
        except Exception as e:
            # Sadece gerçek hataları göster
            if "200" not in str(e):
                st.sidebar.error(f"Bir sorun oluştu: {e}")
            else:
                st.sidebar.success("✅ Kayıt Başarıyla İşlendi!")
                st.rerun()
    else:
        st.sidebar.error("Lütfen şoför ve görev alanlarını doldurun!")

# --- ANA EKRAN TABLO ---
st.markdown("### 📋 Güncel Hareket Listesi")
data = verileri_getir()

if not data.empty:
    st.dataframe(data, use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor veya veriler yükleniyor...")

# Sayfayı el ile yenileme butonu
if st.button("🔄 Listeyi Tazele"):
    st.cache_data.clear()
    st.rerun()
