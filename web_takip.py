import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. BAĞLANTI AYARLARI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h" # Anon Key'in

supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma Takip", layout="wide")

# --- 2. VERİ ÇEKME FONKSİYONLARI ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Şoförleri çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [str(x['ad_soyad']) for x in s_res.data]
        
        # Plakaları çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [str(x['plaka_no']) for x in p_res.data]
    except: pass
    return soforler, plakalar

sofor_listesi, plaka_listesi = listeleri_getir()

# --- 3. ARAYÜZ (YAN PANEL - KAYIT FORMU) ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Detayı")

if st.sidebar.button("KAYDET", type="primary", use_container_width=True):
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
        st.sidebar.success("Kayıt Buluta Gönderildi!")
        st.rerun()
    else:
        st.sidebar.warning("Lütfen şoför seçin ve görev detayı girin!")

# --- 4. ANA PANEL (KAYIT LİSTESİ) ---
st.title("🚗 Sözcü Ulaştırma Görev Takip")

st.subheader("📋 Güncel Görev Listesi")
try:
    # Kayıtlar tablosunu çek ve en yeni en üstte olacak şekilde sırala
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        # Tabloyu daha şık gösterelim
        st.dataframe(df[["tarih", "saat", "sofor", "plaka", "km", "gorev"]], 
                     use_container_width=True, hide_index=True)
        
        # Silme butonu (İsteğe bağlı)
        if st.button("En Son Kaydı Sil"):
            supabase.table("kayitlar").delete().eq("id", df.iloc[0]['id']).execute()
            st.success("Kayıt silindi.")
            st.rerun()
    else:
        st.info("Henüz hiç kayıt girilmemiş.")
except Exception as e:
    st.error(f"Kayıtlar yüklenirken bir sorun oluştu: {e}")

# --- 5. ARAÇ DURUM PANELİ ---
st.divider()
st.subheader("🚙 Araçların Mevcut Durumu")
cols = st.columns(4)
sadece_plakalar = plaka_listesi[1:] # "Seçiniz" kısmını atla

for i in range(1, 9):
    col = cols[(i-1)%4]
    p_adi = sadece_plakalar[i-1] if (i-1) < len(sadece_plakalar) else f"Araç {i}"
    with col:
        st.button(f"{p_adi}\n🟢 Müsait", key=f"arac_{i}", use_container_width=True)
