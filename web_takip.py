import streamlit as st
from supabase import create_client, Client

# --- BAĞLANTI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"

supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Debug", layout="wide")
st.title("🔍 Veri Kontrol Paneli")

# --- CACHE KAPALI (her seferinde DB'den çek) ---
@st.cache_data(ttl=0)
def veri_getir():
    kisiler = supabase.table("kisiler").select("*").execute()
    plaka = supabase.table("plaka").select("*").execute()
    return kisiler, plaka

# --- VERİ ÇEK ---
try:
    s_test, p_test = veri_getir()

    # DEBUG
    st.write("ŞOFÖR DATA:", s_test.data)
    st.write("PLAKA DATA:", p_test.data)

    # ŞOFÖR
    if s_test.data:
        st.success("Şoför verisi geldi ✅")
        sofor_listesi = ["Seçiniz..."] + [x["ad_soyad"] for x in s_test.data]
    else:
        st.warning("⚠️ 'kisiler' tablosu boş!")
        sofor_listesi = ["Seçiniz..."]

    # PLAKA
    if p_test.data:
        st.success("Plaka verisi geldi ✅")
        plaka_listesi = ["Seçiniz..."] + [x["plaka_no"] for x in p_test.data]
    else:
        st.warning("⚠️ 'plaka' tablosu boş!")
        plaka_listesi = ["Seçiniz..."]

except Exception as e:
    st.error(f"KRİTİK HATA: {e}")
    sofor_listesi = ["Seçiniz..."]
    plaka_listesi = ["Seçiniz..."]

# --- SIDEBAR ---
st.sidebar.header("📝 Kayıt Formu")

s_sofor = st.sidebar.selectbox("Şoför", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka", plaka_listesi)

# --- YENİLE BUTONU ---
if st.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()
