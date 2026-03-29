import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI AYARLARI ---
# LÜTFEN: Bu iki bilgiyi Supabase'den taze kopyalayıp buraya tırnak içine yapıştır
URL = "https://rmzfbgaimyuacpovpxm.supabase.co".strip()
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NjMzMjUsImV4cCI6MjA5MDMzOTMyNX0.aZ4pt5km5Ben2YTqENKtrpKoIOTKLMJoGp6NsMtrdxQ".strip()

# Bağlantıyı oluştur (En sağlam yöntemle)
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")

st.set_page_config(page_title="Sözcü Takip Paneli", layout="wide")

# --- VERİ ÇEKME ---
def verileri_yukle():
    try:
        # Tablolara erişmeyi dene
        s_res = supabase.from_("kisiler").select("ad_soyad").execute()
        p_res = supabase.from_("plaka").select("plaka_no").execute()
        k_res = supabase.from_("kayitlar").select("*").order("id", desc=True).execute()
        return s_res.data, p_res.data, k_res.data
    except Exception as e:
        # Eğer hala hata varsa buraya net olarak yazacak
        st.error(f"⚠️ VERİ ÇEKİLEMEDİ: {e}")
        return [], [], []

s_data, p_data, k_data = verileri_yukle()

# --- FORM VE LİSTELER ---
sofor_listesi = ["Seçiniz..."] + [str(x['ad_soyad']) for x in s_data]
plaka_listesi = ["Seçiniz..."] + [str(x['plaka_no']) for x in p_data]

st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# Sol Panel Kayıt Formu
st.sidebar.header("📝 Yeni Kayıt")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Tanımı")

if st.sidebar.button("KAYDET"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Kayıt Başarıyla Gönderildi!")
        st.rerun()

# Ana Ekran Tablo
if k_data:
    df = pd.DataFrame(k_data)
    st.dataframe(df[["tarih", "saat", "sofor", "plaka", "km", "gorev"]], use_container_width=True, hide_index=True)
else:
    st.info("Henüz görüntülenecek kayıt bulunmuyor.")
