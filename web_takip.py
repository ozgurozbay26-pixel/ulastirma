import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- BAĞLANTI ---
URL = "https://rmzfbgaiamyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIpebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma", layout="wide")

# --- VERİ ÇEKME ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [str(x['ad_soyad']) for x in s_res.data]
        
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [str(x['plaka_no']) for x in p_res.data]
    except: pass
    return soforler, plakalar

def son_gorev_oku(p_no):
    try:
        res = supabase.table("kayitlar").select("sofor, gorev").eq("plaka", p_no).order("id", desc=True).limit(1).execute()
        if res.data:
            return f"Şoför: {res.data[0]['sofor']}\nSon Görev: {res.data[0]['gorev']}"
    except: pass
    return "Henüz görev kaydı yok."

sofor_listesi, plaka_listesi = listeleri_getir()

# --- ARAYÜZ (SOL PANEL) ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Detayı")

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
st.title("🚗 Sözcü Ulaştırma Takip Paneli")
try:
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Kayıt tablosu şu an boş.")
except: pass

# --- ARAÇLAR ---
st.divider()
st.subheader("🚙 Araç Durumları")
cols = st.columns(4)
p_sadece = plaka_listesi[1:]

for i in range(1, 9):
    col = cols[(i-1)%4]
    p_adi = p_sadece[i-1] if (i-1) < len(p_sadece) else f"Araç {i}"
    with col:
        # Resim dosyan GitHub'da 'car.png' adındaysa görünecektir
        st.image("car.png", width=80) if i <= len(p_sadece) else st.write("🚗")
        st.button(p_adi, key=f"btn_{i}", help=son_gorev_oku(p_adi), use_container_width=True)
