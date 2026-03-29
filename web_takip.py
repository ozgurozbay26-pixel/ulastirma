import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# BİLGİLER
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc2MzMyNSwiZXhwIjoyMDkwMzM5MzI1fQ.uHZuagGk8UxZlzbweufE_z5VaMZH1AoHyFF7gmdAUY4"

st.set_page_config(page_title="Sözcü Takip Son Kontrol", layout="wide")

try:
    # Boşlukları tamamen siliyoruz
    supabase: Client = create_client(URL.strip(), KEY.strip())
    
    # ÇEKMEYİ DENE
    st.title("🚗 Sistem Durum Raporu")
    
    res = supabase.table("kisiler").select("ad_soyad").execute()
    
    # EĞER BURAYA GELİRSE BAŞARILI OLMUŞTUR
    st.success("✅ İNANILMAZ! BAĞLANTI SONUNDA KURULDU.")
    soforler = ["Seçiniz..."] + [x['ad_soyad'] for x in res.data]
    st.selectbox("Şoför Listesi Test", soforler)
    
except Exception as e:
    st.error("❌ SUPABASE HALA REDDEDİYOR!")
    st.warning(f"Gelen Hata Mesajı: {str(e)}")
    
    if "401" in str(e):
        st.info("İpucu: 401 hatası 'Anahtar Yanlış' demektir. Lütfen Supabase'den anahtarı tekrar kopyalayın.")
    elif "403" in str(e):
        st.info("İpucu: 403 hatası 'Yetki Yok' demektir. RLS ayarlarını kontrol etmeliyiz.")
    else:
        st.info("Farklı bir hata oluştu, lütfen mesajı kontrol edin.")

st.info(f"Koddaki Key Sonu: ...{KEY[-5:]}")
