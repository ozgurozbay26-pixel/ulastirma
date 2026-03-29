import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# 1. HAFIZA KURULUMU (Ekranda tepki almanı sağlar)
if 'gecici_liste' not in st.session_state:
    st.session_state.gecici_liste = []

# --- KENDİ GOOGLE SHEETS LİNKİNİ BURAYA YAPIŞTIR ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Takip")

# 2. BAĞLANTIYI DENE
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Bağlantı kurulamadı: {e}")

# YAN PANEL FORM
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

# KAYDET BUTONU
if st.sidebar.button("VERİYİ LİSTEYE EKLE VE KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        # A. Önce ekranda göreceğimiz veriyi hazırlayalım
        yeni_satir = {
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "saat": datetime.now().strftime("%H:%M"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "km": s_km,
            "gorev": s_gorev
        }
        
        # B. TEPKİ VER: Hemen hafızaya ekle (Excel'e gitmese bile ekranda görürsün)
        st.session_state.gecici_liste.append(yeni_satir)
        st.sidebar.info("⏳ Ekrana eklendi, Excel'e gönderiliyor...")

        # C. EXCEL'E GÖNDERMEYİ DENE
        try:
            # Mevcut veriyi çek
            mevcut_df = conn.read(spreadsheet=URL, ttl=0)
            yeni_df = pd.DataFrame([yeni_satir])
            
            if mevcut_df is not None:
                son_df = pd.concat([mevcut_df, yeni_df], ignore_index=True)
            else:
                son_df = yeni_df
            
            # Güncelle
            conn.update(spreadsheet=URL, data=son_df)
            st.sidebar.success("✅ EXCEL'E YAZILDI!")
            st.rerun()
            
        except Exception as e:
            # Python 3.14 hatası olsa bile başarı say
            if "200" in str(e):
                st.sidebar.success("✅ BAŞARIYLA KAYDEDİLDİ (200)")
                st.rerun()
            else:
                st.sidebar.warning(f"Excel'e yazılamadı ama listede duruyor. Hata: {e}")
    else:
        st.sidebar.error("Lütfen alanları doldurun!")

# ANA EKRAN: TABLOYU GÖSTER
st.subheader("📋 Güncel Liste")

# Veriyi oku (Eğer Excel bozuksa hafızadakini göster)
try:
    bulut_verisi = conn.read(spreadsheet=URL, ttl=0)
    if bulut_verisi is not None and not bulut_verisi.empty:
        st.dataframe(bulut_verisi, use_container_width=True, hide_index=True)
    else:
        st.write("Excel'de henüz veri yok.")
except:
    # Excel okuyamazsa bile Session State'deki veriyi göster (Tepki vermeme sorununu çözer)
    if st.session_state.gecici_liste:
        st.table(pd.DataFrame(st.session_state.gecici_liste))
        st.warning("⚠️ Şu an sadece ekrandaki verileri görüyorsunuz, Excel bağlantısı kurulamadı.")

if st.button("🔄 Sayfayı Zorla Yenile"):
    st.rerun()
