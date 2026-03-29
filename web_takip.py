import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "BURAYA_ANON_KEYI_YAPIŞTIR"

# Supabase istemcisini oluştur
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- VERİ ÇEKME ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # kisiler tablosundan ad_soyad çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [str(x['ad_soyad']) for x in s_res.data]
        
        # plaka tablosundan plaka_no çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [str(x['plaka_no']) for x in p_res.data]
    except Exception as e:
        st.error(f"Veri çekilemedi: {e}")
    return soforler, plakalar

sofor_listesi, plaka_listesi = listeleri_getir()

# --- ARAYÜZ ---
st.title("🚗 Sözcü Ulaştırma - Bulut Paneli")

st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("KM")
s_gorev = st.sidebar.text_area("Görev Detayı")

if st.sidebar.button("Kaydet", type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_kayit = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor,
            "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"),
            "km": s_km,
            "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni_kayit).execute()
        st.sidebar.success("Kayıt başarıyla buluta eklendi!")
        st.rerun()

# --- KAYITLARI GÖSTER ---
st.subheader("📋 Güncel Kayıt Listesi")
try:
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz bir kayıt bulunmuyor.")
except:
    st.error("Kayıtlar tablosuna erişilemedi.")
