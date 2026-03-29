import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI AYARLARI (SENİN VERDİĞİN BİLGİLER) ---
# Sağında solunda boşluk kalmasın diye .strip() ekledim
URL = "https://rmzfbgaimyuacpovpxm.supabase.co".strip()
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc2MzMyNSwiZXhwIjoyMDkwMzM5MzI1fQ.uHZuagGk8UxZlzbweufE_z5VaMZH1AoHyFF7gmdAUY4".strip()

# Bağlantıyı en sağlam şekilde kuralım
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")

st.set_page_config(page_title="Sözcü Takip Paneli", layout="wide")

# --- VERİ ÇEKME ---
def verileri_yukle():
    try:
        # Tablolardan verileri çekiyoruz
        s_res = supabase.from_("kisiler").select("*").execute()
        p_res = supabase.from_("plaka").select("*").execute()
        k_res = supabase.from_("kayitlar").select("*").order("id", desc=True).execute()
        return s_res.data, p_res.data, k_res.data, None
    except Exception as e:
        return [], [], [], str(e)

s_data, p_data, k_data, hata = verileri_yukle()

# --- ARAYÜZ TASARIMI ---
st.title("🚗 Sözcü Ulaştırma Takip")

if hata:
    st.error(f"❌ Supabase Hatası: {hata}")
    st.info("Eğer bu hatayı görüyorsan, Supabase panelinden anahtarları tekrar kontrol etmeliyiz.")
else:
    st.success("✅ BAĞLANTI BAŞARILI! İSİMLER GELDİ.")
    
    # Sol Menü Formu
    st.sidebar.header("📝 Yeni Görev Kaydı")
    soforler = ["Seçiniz..."] + [str(x['ad_soyad']) for x in s_data]
    plakalar = ["Seçiniz..."] + [str(x['plaka_no']) for x in p_data]
    
    s_sofor = st.sidebar.selectbox("Şoför Seçin", soforler)
    s_plaka = st.sidebar.selectbox("Plaka Seçin", plakalar)
    s_km = st.sidebar.text_input("Araç KM")
    s_gorev = st.sidebar.text_area("Görev Detayı")
    
    if st.sidebar.button("KAYDET", type="primary", use_container_width=True):
        if s_sofor != "Seçiniz..." and s_gorev.strip():
            yeni_kayit = {
                "tarih": date.today().strftime("%d.%m.%Y"),
                "sofor": s_sofor,
                "plaka": s_plaka,
                "saat": "00:00",
                "km": s_km,
                "gorev": s_gorev
            }
            supabase.table("kayitlar").insert(yeni_kayit).execute()
            st.sidebar.success("Başarıyla eklendi!")
            st.rerun()

    # Kayıt Tablosu
    if k_data:
        df = pd.DataFrame(k_data)
        st.dataframe(df[["tarih", "sofor", "plaka", "km", "gorev"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("Görüntülenecek kayıt bulunmuyor.")
