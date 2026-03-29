import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# BAĞLANTI BİLGİLERİ (DOĞRUDAN SENİN MASTER KEYİN)
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc2MzMyNSwiZXhwIjoyMDkwMzM5MzI1fQ.uHZuagGk8UxZlzbweufE_z5VaMZH1AoHyFF7gmdAUY4"

# Bağlantıyı kur
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Hareket Takip", layout="wide")

# VERİ ÇEKME
def verileri_al():
    try:
        s = supabase.table("kisiler").select("*").execute()
        p = supabase.table("plaka").select("*").execute()
        k = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s.data, p.data, k.data, None
    except Exception as e:
        return [], [], [], str(e)

s_data, p_data, k_data, hata = verileri_al()

# EKRAN TASARIMI
st.title("🚗 Sözcü Ulaştırma Takip")

if hata:
    st.error(f"Bağlantı Hatası: {hata}")
    st.info(f"Koddaki Key Sonu: ...{KEY[-5:]}") # Burada UY4 görmeliyiz!
else:
    st.sidebar.header("📝 Yeni Kayıt")
    soforler = ["Seçiniz..."] + [x['ad_soyad'] for x in s_data]
    plakalar = ["Seçiniz..."] + [x['plaka_no'] for x in p_data]
    
    s_sofor = st.sidebar.selectbox("Şoför", soforler)
    s_plaka = st.sidebar.selectbox("Plaka", plakalar)
    s_km = st.sidebar.text_input("KM")
    s_gorev = st.sidebar.text_area("Görev")
    
    if st.sidebar.button("KAYDET"):
        if s_sofor != "Seçiniz..." and s_gorev:
            yeni = {
                "tarih": date.today().strftime("%d.%m.%Y"),
                "sofor": s_sofor, "plaka": s_plaka,
                "saat": "00:00", "km": s_km, "gorev": s_gorev
            }
            supabase.table("kayitlar").insert(yeni).execute()
            st.rerun()

    if k_data:
        st.dataframe(pd.DataFrame(k_data)[["tarih", "sofor", "plaka", "km", "gorev"]], use_container_width=True)
