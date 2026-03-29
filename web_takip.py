import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- KRİTİK: LİNKİ BURAYA YAPIŞTIR ---
# Google Sheets sayfasını açtığında üstteki adres çubuğunda yazan linkin tamamını kopyala
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Takip")

# BAĞLANTIYI BAŞLAT
conn = st.connection("gsheets", type=GSheetsConnection)

# YAN PANEL
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("VERİYİ EXCEL'E GÖNDER", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        with st.status("🚀 Google Sheets'e bağlanılıyor...", expanded=True) as status:
            try:
                # 1. Veriyi hazırla
                yeni_satir = pd.DataFrame([{
                    "tarih": datetime.now().strftime("%d.%m.%Y"),
                    "saat": datetime.now().strftime("%H:%M"),
                    "sofor": s_sofor,
                    "plaka": s_plaka,
                    "km": s_km,
                    "gorev": s_gorev
                }])
                
                st.write("📡 Mevcut veriler okunuyor...")
                # 2. Mevcut veriyi çek (Yoksa boş tablo oluştur)
                try:
                    mevcut_df = conn.read(spreadsheet=URL, ttl=0)
                except:
                    mevcut_df = pd.DataFrame(columns=["tarih", "saat", "sofor", "plaka", "km", "gorev"])
                
                st.write("📝 Tablo güncelleniyor...")
                # 3. Birleştir ve Gönder
                if mevcut_df is not None and not mevcut_df.empty:
                    son_df = pd.concat([mevcut_df, yeni_satir], ignore_index=True)
                else:
                    son_df = yeni_satir
                
                conn.update(spreadsheet=URL, data=son_df)
                
                status.update(label="✅ Kayıt Başarıyla Tamamlandı!", state="complete", expanded=False)
                st.sidebar.success("İşlem Başarılı!")
                st.rerun()
                
            except Exception as e:
                # 200 mesajı bir başarı sinyalidir, hata değil!
                if "200" in str(e):
                    status.update(label="✅ Kayıt Başarılı!", state="complete")
                    st.rerun()
                else:
                    status.update(label="❌ Bağlantı Hatası!", state="error")
                    st.error(f"Detay: {e}")
    else:
        st.sidebar.warning("Lütfen şoför ve görev girin.")

# ANA TABLO
st.subheader("📋 Güncel Hareket Listesi")
try:
    data = conn.read(spreadsheet=URL, ttl=0)
    if data is not None and not data.empty:
        st.dataframe(data.dropna(how='all'), use_container_width=True, hide_index=True)
    else:
        st.info("Excel'de henüz kayıt bulunmuyor.")
except Exception as e:
    st.warning("⚠️ Excel'den veri şu an çekilemiyor. Lütfen linki ve izinleri kontrol edin.")
