import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Sözcü Ulaştırma Takip", layout="wide")

# --- 1. BAĞLANTI AYARLARI (SECRETS) ---
try:
    # Streamlit Secrets'taki JSON bilgilerini alıyoruz
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Secrets içindeki [connections.gsheets] altındaki bilgileri çekiyoruz
    creds_info = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    # --- BURAYA KENDİ LİNKİNİ YAPIŞTIR ---
    URL = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
    sheet = client.open_by_url(URL).sheet1 # İlk sayfayı açar

except Exception as e:
    st.error(f"⚠️ Bağlantı Kurulamadı: {e}")
    st.stop()

# --- 2. ARAYÜZ VE KAYIT ---
st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

st.sidebar.header("📝 Yeni Kayıt")
soforler = ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"]
plakalar = ["Seçiniz...", "34 ABC 123", "06 XYZ 789"]

s_sofor = st.sidebar.selectbox("Şoför", soforler)
s_plaka = st.sidebar.selectbox("Plaka", plakalar)
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        try:
            # Veriyi listeye çevirip en alta ekliyoruz
            yeni_satir = [
                datetime.now().strftime("%d.%m.%Y"),
                datetime.now().strftime("%H:%M"),
                s_sofor,
                s_plaka,
                s_km,
                s_gorev
            ]
            sheet.append_row(yeni_satir)
            st.sidebar.success("✅ Veritabanına Kaydedildi!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Kayıt hatası: {e}")
    else:
        st.sidebar.warning("Lütfen alanları doldurun.")

# --- 3. VERİLERİ GÖSTER ---
st.subheader("📋 3 Yıllık Hareket Arşivi")
try:
    # Tüm verileri çekip tabloya basıyoruz
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz arşivde kayıt bulunmuyor.")
except Exception as e:
    st.warning("Veriler şu an listelenemiyor.")

if st.button("🔄 Arşivi Yenile"):
    st.rerun()
