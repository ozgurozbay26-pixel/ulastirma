import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- 2. VERİ ÇEKME (EKSTRA SAĞLAM) ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Şoförleri çek - tablo adını tam olarak buraya yazıyoruz
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [str(x['ad_soyad']) for x in s_res.data]
        
        # Plakaları çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [str(x['plaka_no']) for x in p_res.data]
    except Exception as e:
        # Hata varsa buraya yazacak
        st.error(f"Tabloya ulaşılamadı: {e}")
    return soforler, plakalar

sofor_listesi, plaka_listesi = listeleri_getir()

# --- 3. FORM ---
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("KAYDET", type="primary", use_container_width=True):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Kaydedildi!")
        st.rerun()

# --- 4. ANA EKRAN ---
st.title("🚗 Sözcü Ulaştırma Takip")
try:
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Kayıtlar tablosu şu an boş.")
except: pass
