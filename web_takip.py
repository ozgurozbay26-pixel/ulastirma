import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- KONTROL EDİLMİŞ BAĞLANTI BİLGİLERİ ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"

# Bağlantıyı başlat
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=0) # Verileri her dakika tazelemesi için
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Şoförleri çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [str(x['ad_soyad']) for x in s_res.data if x.get('ad_soyad')]
        
        # Plakaları çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [str(x['plaka_no']) for x in p_res.data if x.get('plaka_no')]
            
    except Exception as e:
        st.error(f"Veri Çekme Hatası: {e}")
    return soforler, plakalar

def son_gorev_oku(plaka_adi):
    try:
        res = supabase.table("kayitlar").select("sofor, gorev").eq("plaka", plaka_adi).order("id", desc=True).limit(1).execute()
        if res.data:
            return f"Şoför: {res.data[0]['sofor']}\nGörev: {res.data[0]['gorev']}"
    except: pass
    return "Kayıt bulunamadı."

# Listeleri yükle
sofor_listesi, plaka_listesi = listeleri_getir()

# --- SOL PANEL ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev")

if st.sidebar.button("Kaydet", use_container_width=True, type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni).execute()
        st.sidebar.success("Buluta Kaydedildi!")
        st.rerun()

# --- ANA PANEL ---
st.title("🚗 Sözcü Ulaştırma")
try:
    res_k = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(res_k.data)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
except: pass

# --- ARAÇLAR ---
st.divider()
cols = st.columns(4)
p_sadece = plaka_listesi[1:]
for i in range(1, 9):
    col = cols[(i-1)%4]
    p_ismi = p_sadece[i-1] if (i-1) < len(p_sadece) else f"Araç {i}"
    with col:
        st.button(p_ismi, key=f"btn_{i}", help=son_gorev_oku(p_ismi), use_container_width=True)
