import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- KENDİ LİNKİNİ BURAYA YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

# Bağlantıyı Kur
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# Yan Panel Formu
st.sidebar.header("📝 Yeni Hareket Kaydı")
soforler = ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"]
plakalar = ["Seçiniz...", "34 ABC 123", "06 XYZ 789"]

s_sofor = st.sidebar.selectbox("Şoför Seçin", soforler)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plakalar)
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_veri = pd.DataFrame([{
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }])
        
        try:
            # TTL=0 ekleyerek hafızayı zorla tazeliyoruz
            df = conn.read(spreadsheet=URL, ttl=0)
            if df is not None and not df.empty:
                updated_df = pd.concat([df, yeni_veri], ignore_index=True)
            else:
                updated_df = yeni_veri
            
            conn.update(spreadsheet=URL, data=updated_df)
            st.sidebar.success("Kayıt Excel'e işlendi!")
            st.cache_data.clear() # Önbelleği temizle
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Kayıt sırasında hata: {e}")
    else:
        st.sidebar.error("Lütfen tüm alanları doldurun!")

# --- VERİLERİ GÖRÜNTÜLEME (GÜVENLİ MOD) ---
st.markdown("### 📋 Güncel Hareket Listesi")

try:
    # TTL=0 verinin anında görünmesini sağlar
    data = conn.read(spreadsheet=URL, ttl=0)
    
    if data is not None and not data.empty:
        # Tabloyu gösterirken hatalı satırları (boş olanları) temizle
        data = data.dropna(how='all')
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kayıt bulunmuyor. İlk kaydı sol taraftan girebilirsiniz.")
except Exception as e:
    # Eğer o NoneType hatası tekrar ederse site çökmeyecek, bu mesajı verecek
    st.warning("Veriler şu an yüklenemiyor, lütfen bir saniye sonra sayfayı yenileyin.")
    # Teknik detay görmek istersen: st.write(e)
