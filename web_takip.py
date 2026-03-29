import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "BURAYA_SUPABASE_API_AYARLARINDAKI_ANON_KEYI_YAPISTIR" 

supabase: Client = create_client(URL, KEY)

st.title("Sözcü Ulaştırma Test Paneli")

# --- TEST SORGUSU ---
try:
    # Direkt kisiler tablosunu çekmeyi deniyoruz
    test_sorgu = supabase.table("kisiler").select("*").execute()
    
    if test_sorgu.data:
        st.success(f"BAŞARILI! {len(test_sorgu.data)} adet şoför bulundu.")
        st.write("Gelen Veriler:", test_sorgu.data)
        
        # Listeye aktaralım
        isimler = [x['ad_soyad'] for x in test_sorgu.data]
        st.selectbox("Şoför Listesi Testi", isimler)
    else:
        st.error("BAĞLANTI VAR AMA TABLO BOŞ GÖRÜNÜYOR!")
        st.info("Lütfen Supabase'de verileri girdikten sonra SAVE butonuna bastığınızdan emin olun.")

except Exception as e:
    st.error(f"EYVAH! BİR HATA VAR: {e}")
