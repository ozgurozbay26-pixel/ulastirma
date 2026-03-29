import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. BAĞLANTI AYARLARI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtemZiZ2FpYW15dWFjcG92cHhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NjMzMjUsImV4cCI6MjA5MDMzOTMyNX0.aZ4pt5km5Ben2YTqENKtrpKoIOTKLMJoGp6NsMtrdxQ"

# Bağlantıyı kur
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Sözcü Ulaştırma Takip", layout="wide", page_icon="🚗")

# --- 2. VERİ ÇEKME FONKSİYONU ---
def verileri_yukle():
    try:
        # Şoförleri, Plakaları ve Kayıtları çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        p_res = supabase.table("plaka").select("plaka_no").execute()
        k_res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
        return s_res.data, p_res.data, k_res.data
    except Exception as e:
        return [], [], []

s_data, p_data, k_data = verileri_yukle()

# --- 3. YAN PANEL (KAYIT FORMU) ---
st.sidebar.markdown("### 📝 Yeni Görev Kaydı")
sofor_listesi = ["Seçiniz..."] + [str(x['ad_soyad']) for x in s_data]
plaka_listesi = ["Seçiniz..."] + [str(x['plaka_no']) for x in p_data]

s_sofor = st.sidebar.selectbox("Şoför Seçin", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM", placeholder="Örn: 145200")
s_gorev = st.sidebar.text_area("Görev Tanımı", placeholder="Gidilecek yer...")

if st.sidebar.button("KAYDET VE LİSTEYE EKLE", type="primary", use_container_width=True):
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
        st.sidebar.success("Kayıt başarıyla eklendi!")
        st.rerun()
    else:
        st.sidebar.error("Lütfen şoför seçin ve görev yazın!")

# --- 4. ANA EKRAN (TABLO VE DURUM) ---
st.title("🚗 Sözcü Ulaştırma Hareket Takibi")

# Özet Bilgiler
c1, c2 = st.columns(2)
c1.metric("Toplam Hareket", len(k_data))
c2.metric("Sistemdeki Şoför", len(s_data))

st.markdown("---")
st.subheader("📋 Güncel Hareket Listesi")

if k_data:
    df = pd.DataFrame(k_data)
    # Tabloyu düzenli sütunlarla göster
    st.dataframe(df[["tarih", "saat", "sofor", "plaka", "km", "gorev"]], 
                 use_container_width=True, hide_index=True)
else:
    st.info("Şu an görüntülenecek bir kayıt bulunmuyor.")

# --- 5. ARAÇ DURUM PANELİ ---
st.divider()
st.subheader("🚙 Araç Filosu")
cols = st.columns(4)
p_temiz = plaka_listesi[1:] # "Seçiniz"i atla

for i in range(1, 9):
    with cols[(i-1)%4]:
        p_ismi = p_temiz[i-1] if (i-1) < len(p_temiz) else f"Araç {i}"
        st.button(f"{p_ismi}\n🟢 Müsait", key=f"arac_{i}", use_container_width=True)
