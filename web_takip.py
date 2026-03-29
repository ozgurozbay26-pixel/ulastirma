import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- SUPABASE BAĞLANTI AYARLARI ---
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h" # Senin kopyaladığın anahtar

supabase: Client = create_client(URL, KEY)

# Sayfa Ayarları
st.set_page_config(page_title="Sözcü Ulaştırma Bulut", layout="wide")

# --- HAFIZA (Araç Durumları) ---
if 'arac_durumu' not in st.session_state:
    st.session_state['arac_durumu'] = {i: True for i in range(1, 9)}

def durum_degistir(arac_id):
    st.session_state['arac_durumu'][arac_id] = not st.session_state['arac_durumu'][arac_id]

# --- VERİ ÇEKME FONKSİYONLARI ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # Buluttan verileri çekiyoruz
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        soforler += [x['ad_soyad'] for x in s_res.data]
        p_res = supabase.table("plaka").select("plaka_no").execute()
        plakalar += [x['plaka_no'] for x in p_res.data]
    except: pass
    return soforler, plakalar

def son_gorev_oku(p):
    try:
        res = supabase.table("kayitlar").select("sofor, gorev").eq("plaka", p).order("id", desc=True).limit(1).execute()
        if res.data: return f"Şoför: {res.data[0]['sofor']}\nGörev: {res.data[0]['gorev']}"
    except: pass
    return "Görev bilgisi yok."

sofor_listesi, plaka_listesi = listeleri_getir()

# --- FORM BÖLÜMÜ ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin (*)", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat Seçin")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Detayı (*)")

if st.sidebar.button("Kaydet", use_container_width=True, type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        yeni_veri = {
            "tarih": date.today().strftime("%d.%m.%Y"),
            "sofor": s_sofor, "plaka": s_plaka,
            "saat": s_saat.strftime("%H:%M"), "km": s_km, "gorev": s_gorev
        }
        supabase.table("kayitlar").insert(yeni_veri).execute()
        st.sidebar.success("Bulut Veritabanına Kaydedildi!")
        st.rerun()
    else: st.sidebar.warning("Lütfen zorunlu alanları doldurun!")

# --- ANA EKRAN ---
st.title("🚗 Sözcü Ulaştırma (Bulut Sistemi)")
res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
df = pd.DataFrame(res.data)

if not df.empty:
    st.subheader(f"📋 Kayıtlar (Toplam: {len(df)})")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("En Son Kaydı Sil"):
        supabase.table("kayitlar").delete().eq("id", df.iloc[0]['id']).execute()
        st.rerun()
else:
    st.info("Henüz kayıt bulunamadı. Lütfen formdan yeni bir görev ekleyin.")

# --- ARAÇ PANELİ ---
st.divider()
st.subheader("🚙 Araç Durum Paneli")
cols = st.columns(4)
gercek_plakalar = plaka_listesi[1:] # "Seçiniz"i atla

for i in range(1, 9):
    col = cols[(i-1)%4]
    p_adi = gercek_plakalar[i-1] if (i-1) < len(gercek_plakalar) else f"Araç {i}"
    durum = st.session_state['arac_durumu'][i]
    with col:
        st.button(f"{p_adi}\n{'🟢 Müsait' if durum else '🔴 Görevde'}", 
                  key=f"arac_{i}", on_click=durum_degistir, args=(i,),
                  help=son_gorev_oku(p_adi), use_container_width=True)
