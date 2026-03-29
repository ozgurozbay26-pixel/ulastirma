import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Debug", layout="wide")
st.title("🔍 Veri Kontrol Paneli")

# --- VERİ ÇEKMEYİ DENE ---
try:
    # 1. Şoförleri çekmeyi dene
    s_test = supabase.table("kisiler").select("*").execute()
    st.write("Şoför Verisi Geldi mi?:", "EVET ✅" if s_test.data else "HAYIR ❌")
    
    # 2. Plakaları çekmeyi dene
    p_test = supabase.table("plaka").select("*").execute()
    st.write("Plaka Verisi Geldi mi?:", "EVET ✅" if p_test.data else "HAYIR ❌")

    if s_test.data:
        st.success(f"Bulunan Şoförler: {[x['ad_soyad'] for x in s_test.data]}")
        sofor_listesi = ["Seçiniz..."] + [x['ad_soyad'] for x in s_test.data]
    else:
        st.warning("Veritabanı bağlandı ama 'kisiler' tablosu boş dönüyor!")
        sofor_listesi = ["Seçiniz..."]

    if p_test.data:
        plaka_listesi = ["Seçiniz..."] + [x['plaka_no'] for x in p_test.data]
    else:
        plaka_listesi = ["Seçiniz..."]

except Exception as e:
    st.error(f"⚠️ KRİTİK HATA: {e}")
    sofor_listesi = ["Seçiniz..."]
    plaka_listesi = ["Seçiniz..."]

# --- ARAYÜZ ---
st.sidebar.header("📝 Kayıt Formu")
s_sofor = st.sidebar.selectbox("Şoför", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka", plaka_listesi)
