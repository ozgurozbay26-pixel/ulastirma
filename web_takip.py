import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
# BURAYA SUPABASE'DEN ALDIĞIN eyJ... İLE BAŞLAYAN ÇOK UZUN ANON KEY'İ YAPIŞTIR
KEY = "BURAYA_GERCEK_KEYINI_YAPISTIR" 

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı kurulamadı: {e}")

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- VERİ ÇEKME ---
def verileri_yukle():
    try:
        # Hata ayıklama için direkt sorgu
        s_res = supabase.table("kisiler").select("*").execute()
        p_res = supabase.table("plaka").select("*").execute()
        k_res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s_res.data, p_res.data, k_res.data
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return [], [], []

s_data, p_data, k_data = verileri_yukle()

# --- LİSTELER ---
sofor_listesi = ["Seçiniz..."] + [str(x['ad_soyad']) for x in s_data]
plaka_listesi = ["Seçiniz..."] + [str(x['plaka_no']) for x in p_data]

# --- ARAYÜZ ---
st.title("🚗 Sözcü Ulaştırma Görev Takip")

# Sol Menü Form
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Detayı")

if st.sidebar.button("KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Başarıyla Kaydedildi!")
        st.rerun()

# Ana Ekran Tablo
if k_data:
    df = pd.DataFrame(k_data)
    st.dataframe(df[["tarih", "saat", "sofor", "plaka", "km", "gorev"]], use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt bulunmuyor.")
