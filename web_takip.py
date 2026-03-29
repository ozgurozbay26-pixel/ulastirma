import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- VERİ ÇEKME (RESİMDE ÇALIŞAN YÖNTEM) ---
def verileri_al():
    try:
        # Az önce resimde çalışan sorgu buydu: select("*")
        s_sorgu = supabase.table("kisiler").select("*").execute()
        p_sorgu = supabase.table("plaka").select("*").execute()
        k_sorgu = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s_sorgu.data, p_sorgu.data, k_sorgu.data
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return [], [], []

s_data, p_data, k_data = verileri_al()

# --- LİSTELERİ HAZIRLA ---
# Eğer veri geldiyse listeye ekle, gelmediyse sadece 'Seçiniz' kalsın
sofor_list = ["Seçiniz..."] + [x['ad_soyad'] for x in s_data if 'ad_soyad' in x]
plaka_list = ["Seçiniz..."] + [x['plaka_no'] for x in p_data if 'plaka_no' in x]

# --- ARAYÜZ ---
st.title("🚗 Sözcü Ulaştırma Takip")

# Sol Tarafta Form
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför Seç", sofor_list)
s_plaka = st.sidebar.selectbox("Plaka Seç", plaka_list)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Kaydedildi!")
        st.rerun()

# Ana Ekranda Tablo
if k_data:
    st.markdown("### 📋 Görev Listesi")
    st.dataframe(pd.DataFrame(k_data), use_container_width=True, hide_index=True)
else:
    st.info("Henüz kayıt yok veya veritabanı boş.")
