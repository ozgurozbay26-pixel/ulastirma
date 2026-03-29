import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. BAĞLANTI (LÜTFEN SERVICE_ROLE KEY'İ YAPIŞTIR) ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
# Buraya az önce aldığın 'service_role' anahtarını yapıştır
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc2MzMyNSwiZXhwIjoyMDkwMzM5MzI1fQ.uHZuagGk8UxZlzbweufE_z5VaMZH1AoHyFF7gmdAUY4" 

# Bağlantıyı kur (Hafızayı temizlemek için cache kullanmıyoruz)
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Takip", layout="wide")

# --- 2. VERİ ÇEKME ---
# Cache (hafıza) fonksiyonunu tamamen kaldırdık!
def verileri_yukle():
    try:
        s = supabase.table("kisiler").select("*").execute()
        p = supabase.table("plaka").select("*").execute()
        k = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s.data, p.data, k.data
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        return [], [], []

s_data, p_data, k_data = verileri_yukle()

# --- 3. LİSTELER ---
soforler = ["Seçiniz..."] + [str(x['ad_soyad']) for x in s_data]
plakalar = ["Seçiniz..."] + [str(x['plaka_no']) for x in p_data]

# --- 4. ARAYÜZ ---
st.title("🚗 Sözcü Ulaştırma Takip")

if not s_data:
    st.warning("Veritabanına ulaşıldı ama şoför listesi boş dönüyor. SQL ile eklediğinden emin ol!")

# Sol Panel
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför", soforler)
s_plaka = st.sidebar.selectbox("Plaka", plakalar)
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
        st.sidebar.success("Kayıt Başarılı!")
        st.rerun()

# Ana Tablo
if k_data:
    st.dataframe(pd.DataFrame(k_data)[["tarih", "saat", "sofor", "plaka", "km", "gorev"]], 
                 use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor.")
