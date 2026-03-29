import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- KESİN VE NET BİLGİLER ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
# Senin az önce gönderdiğin "Master Key" (Yönetici Anahtarı)
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc2MzMyNSwiZXhwIjoyMDkwMzM5MzI1fQ.uHZuagGk8UxZlzbweufE_z5VaMZH1AoHyFF7gmdAUY4"

# Bağlantıyı her seferinde sıfırdan kurmaya zorlayalım
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Takip Denetim", layout="wide")

# --- TEŞHİS PANELİ (HATA VARSA BURADA GÖRECEĞİZ) ---
st.title("🕵️ Sistem Denetim Masası")

def verileri_cek():
    try:
        # Deneme amaçlı çok basit bir çekim yapalım
        s = supabase.table("kisiler").select("*").execute()
        p = supabase.table("plaka").select("*").execute()
        k = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s.data, p.data, k.data, None
    except Exception as e:
        return [], [], [], str(e)

s_data, p_data, k_data, hata_mesaji = verileri_cek()

# Eğer hala hata varsa burası yanacak
if hata_mesaji:
    st.error(f"❌ Supabase Reddediyor: {hata_mesaji}")
    st.info(f"Sistemin kullandığı URL: {URL}")
    st.info(f"Sistemin kullandığı Key Sonu: ...{KEY[-10:]}")
    st.warning("EĞER YUKARIDAKİ KEY SONU SENİN ANAHTARINLA AYNI DEĞİLSE, GITHUB GÜNCELLENMEMİŞTİR!")
else:
    st.success("✅ BAĞLANTI BAŞARILI! VERİLER GELİYOR.")

# --- ARAYÜZ (GİZLİ FORM) ---
if not hata_mesaji:
    st.sidebar.header("📝 Yeni Kayıt")
    soforler = ["Seçiniz..."] + [x['ad_soyad'] for x in s_data]
    plakalar = ["Seçiniz..."] + [x['plaka_no'] for x in p_data]
    
    s_sofor = st.sidebar.selectbox("Şoför", soforler)
    s_plaka = st.sidebar.selectbox("Plaka", plakalar)
    s_gorev = st.sidebar.text_area("Görev")
    
    if st.sidebar.button("KAYDET"):
        if s_sofor != "Seçiniz..." and s_gorev:
            yeni = {"tarih": date.today().strftime("%d.%m.%Y"), "sofor": s_sofor, "plaka": s_plaka, "saat": "00:00", "km": "0", "gorev": s_gorev}
            supabase.table("kayitlar").insert(yeni).execute()
            st.rerun()

    # Tablo
    if k_data:
        st.dataframe(pd.DataFrame(k_data), use_container_width=True)
