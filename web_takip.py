import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. BAĞLANTI (LÜTFEN BURAYI KONTROL ET) ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h" # Bu senin Anon Key'in olmalı

# Bağlantıyı kurmaya çalışıyoruz
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- 2. VERİ ÇEKME (HATA MESAJLI) ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Şoförleri Çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [x['ad_soyad'] for x in s_res.data]
        else:
            st.warning("Veritabanında şoför kaydı bulunamadı (Tablo boş mu?)")

        # Plakaları Çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [x['plaka_no'] for x in p_res.data]
        else:
            st.warning("Veritabanında plaka kaydı bulunamadı.")
            
    except Exception as e:
        st.error(f"Supabase Hatası: {e}") # Hata varsa ekranda kırmızıyla yazacak
    return soforler, plakalar

sofor_listesi, plaka_listesi = listeleri_getir()

# --- 3. ARAYÜZ (FORM) ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("Kaydet", use_container_width=True, type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Kaydedildi!")
        st.rerun()

# --- 4. TABLO VE ARAÇLAR ---
st.title("🚗 Sözcü Ulaştırma Takip")
try:
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Kayıt tablosu şu an boş.")
except:
    st.error("Kayıtlar tablosu okunamadı.")
