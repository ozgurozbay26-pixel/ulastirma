import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# Bağlantı Bilgilerin
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"
supabase: Client = create_client(URL, KEY)

def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Şoförleri çek ve hata var mı bak
        s_res = supabase.table("kisiler").select("*").execute()
        if s_res.data:
            # Sütun isminden emin olalım, eğer 'ad_soyad' yoksa gelen tüm datayı bas
            soforler += [str(x.get('ad_soyad', 'Sütun Hatası')) for x in s_res.data]
        
        # Plakaları çek
        p_res = supabase.table("plaka").select("*").execute()
        if p_res.data:
            plakalar += [str(x.get('plaka_no', 'Sütun Hatası')) for x in p_res.data]
            
    except Exception as e:
        st.error(f"Bağlantı Var Ama Veri Çekilemedi: {e}")
    return soforler, plakalar

# Sayfa yüklendiğinde listeleri al
sofor_listesi, plaka_listesi = listeleri_getir()

# Eğer hala 'Seçiniz...' dışında bir şey yoksa uyarı ver
if len(sofor_listesi) <= 1:
    st.sidebar.error("⚠️ Supabase 'kisiler' tablosundan veri okuyamadı! Tabloyu ve RLS ayarını kontrol edin.")

# --- GERİ KALAN FORM VE ARAÇ KODLARI BURAYA GELECEK ---
# (Önceki mesajdaki form kodlarını altına ekleyebilirsin)
