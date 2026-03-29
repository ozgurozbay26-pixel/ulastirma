import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time

st.set_page_config(page_title="Sözcü Takip Sistemi", layout="wide")

# --- 1. BAĞLANTI AYARLARI ---
@st.cache_resource
def gsheet_baglan():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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
    url = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
    return client.open_by_url(url)

try:
    doc = gsheet_baglan()
    sheet_kayitlar = doc.get_worksheet(0)
    
    # LİSTELERİ EXCEL'DEN ÇEK
    def liste_getir(sayfa_adi):
        try:
            temp_sheet = doc.worksheet(sayfa_adi)
            return sorted(temp_sheet.col_values(1)[1:])
        except:
            return ["Sayfa Bulunamadı!"]

    sofor_listesi = liste_getir("soforler")
    arac_listesi = liste_getir("araclar")
    durum_listesi = liste_getir("durum") # YENİ: Durum listesi

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 2. YAN PANEL (GİRİŞ) ---
st.sidebar.header("📝 Yeni Hareket Girişi")
s_tarih = st.sidebar.date_input("Tarih", datetime.now())
s_saat = st.sidebar.time_input("Saat Seçimi", time(12, 0))
s_sofor = st.sidebar.selectbox("Şoför Seçin", ["Seçiniz..."] + sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", ["Seçiniz..."] + arac_listesi)
s_km = st.sidebar.text_input("Araç KM")

# YENİ: GÖREVDEN ÖNCE DURUM SEÇİMİ
s_durum = st.sidebar.selectbox("Hareket Durumu", ["Seçiniz..."] + durum_listesi)

s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("VERİTABANINA KAYDET", type="primary"):
    if s_sofor != "Seçiniz..." and s_plaka != "Seçiniz..." and s_durum != "Seçiniz..." and s_gorev.strip():
        yeni_satir = [
            s_tarih.strftime("%d.%m.%Y"),
            s_saat.strftime("%H:%M"),
            s_sofor,
            s_plaka,
            s_km,
            s_gorev,
            s_durum # 7. Sütun olarak Excel'e gider
        ]
        sheet_kayitlar.append_row(yeni_satir)
        st.sidebar.success("✅ Arşive Kaydedildi!")
        st.cache_data.clear()
        st.rerun()
    else:
        st.sidebar.error("Lütfen Durum dahil tüm alanları doldurun.")

# --- 3. ANA EKRAN ---
st.title("🚗 Sözcü Ulaştırma Hareket Arşivi")

try:
    data = sheet_kayitlar.get_all_records()
    df = pd.DataFrame(data)
except:
    df = pd.DataFrame()

if not df.empty:
    st.markdown("### 🔍 Detaylı Sorgulama")
    c1, c2, c3, c4 = st.columns(4) # 4 sütun yaptık
    with c1: f_sofor = st.multiselect("Şoföre Göre", options=df["sofor"].unique() if "sofor" in df else [])
    with c2: f_plaka = st.multiselect("Plakaya Göre", options=df["plaka"].unique() if "plaka" in df else [])
    with c3: f_tarih = st.multiselect("Tarihe Göre", options=df["tarih"].unique() if "tarih" in df else [])
    with c4: f_durum = st.multiselect("Duruma Göre", options=df["durum"].unique() if "durum" in df else [])

    f_df = df.copy()
    if f_sofor: f_df = f_df[f_df["sofor"].isin(f_sofor)]
    if f_plaka: f_df = f_df[f_df["plaka"].isin(f_plaka)]
    if f_tarih: f_df = f_df[f_df["tarih"].isin(f_tarih)]
    if f_durum: f_df = f_df[f_df["durum"].isin(f_durum)]

    st.write(f"📊 Toplam {len(f_df)} kayıt bulundu.")
    st.dataframe(f_df, use_container_width=True, hide_index=True)
else:
    st.info("Sistem hazır, kayıt yapıldığında burada listelenecek.")

if st.button("🔄 Verileri ve Listeleri Yenile"):
    st.cache_data.clear()
    st.rerun()
