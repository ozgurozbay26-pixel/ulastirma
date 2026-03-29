import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# --- 1. SUPABASE BAĞLANTI AYARLARI ---
# Senin projene özel anahtarlar
URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"

supabase: Client = create_client(URL, KEY)

# Sayfa Ayarları
st.set_page_config(page_title="Sözcü Ulaştırma Bulut", layout="wide")

# --- 2. ARAÇ DURUM HAFIZASI ---
if 'arac_durumu' not in st.session_state:
    st.session_state['arac_durumu'] = {i: True for i in range(1, 9)}

def durum_degistir(arac_id):
    st.session_state['arac_durumu'][arac_id] = not st.session_state['arac_durumu'][arac_id]

# --- 3. BULUTTAN VERİ ÇEKME FONKSİYONLARI ---
def listeleri_getir():
    soforler, plakalar = ["Seçiniz..."], ["Seçiniz..."]
    try:
        # kisiler tablosundan veriyi çek
        s_res = supabase.table("kisiler").select("ad_soyad").execute()
        if s_res.data:
            soforler += [x['ad_soyad'] for x in s_res.data]
        
        # plaka tablosundan veriyi çek
        p_res = supabase.table("plaka").select("plaka_no").execute()
        if p_res.data:
            plakalar += [x['plaka_no'] for x in p_res.data]
    except Exception as e:
        # Eğer bir hata varsa ekranın altında kırmızıyla yazar, sorunu anlarız
        st.error(f"Veri çekme hatası: {e}")
    return soforler, plakalar

def son_gorev_bilgisi(p_no):
    try:
        res = supabase.table("kayitlar").select("sofor, gorev").eq("plaka", p_no).order("id", desc=True).limit(1).execute()
        if res.data:
            return f"Şoför: {res.data[0]['sofor']}\nSon Görev: {res.data[0]['gorev']}"
        return "Bu araca ait kayıt yok."
    except:
        return "Bilgi alınamadı."

sofor_listesi, plaka_listesi = listeleri_getir()

# --- 4. SOL PANEL (KAYIT FORMU) ---
st.sidebar.header("📝 Yeni Görev Kaydı")
s_sofor = st.sidebar.selectbox("Şoför Seçin (*)", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)
s_saat = st.sidebar.time_input("Saat")
s_km = st.sidebar.text_input("Araç KM")
s_gorev = st.sidebar.text_area("Görev Detayı (*)")

if st.sidebar.button("Buluta Kaydet", use_container_width=True, type="primary"):
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        try:
            yeni_veri = {
                "tarih": date.today().strftime("%d.%m.%Y"),
                "sofor": s_sofor,
                "plaka": s_plaka,
                "saat": s_saat.strftime("%H:%M"),
                "km": s_km,
                "gorev": s_gorev
            }
            supabase.table("kayitlar").insert(yeni_veri).execute()
            st.sidebar.success("Kayıt Başarıyla Buluta Gönderildi!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Hata: {e}")
    else:
        st.sidebar.warning("Zorunlu alanları doldurun!")

# --- 5. ANA PANEL (TABLO) ---
st.title("🚗 Sözcü Ulaştırma (Bulut Sistemi)")

# Buluttan tüm kayıtları çek
try:
    res = supabase.table("kayitlar").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
except:
    df = pd.DataFrame()

if not df.empty:
    st.subheader(f"📋 Güncel Kayıtlar (Toplam: {len(df)})")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Silme İşlemi (En üstteki/en son kaydı siler)
    if st.button("En Son Kaydı Sil"):
        supabase.table("kayitlar").delete().eq("id", df.iloc[0]['id']).execute()
        st.rerun()
else:
    st.info("Bulut veritabanında henüz kayıt yok. Lütfen sol taraftan ilk kaydı ekleyin.")

# --- 6. ARAÇ DURUM PANELİ ---
st.divider()
st.subheader("🚙 Araç Durum Paneli")
cols = st.columns(4)
gercek_plakalar = plaka_listesi[1:] # "Seçiniz"i listeden at

for i in range(1, 9):
    col = cols[(i-1)%4]
    p_adi = gercek_plakalar[i-1] if (i-1) < len(gercek_plakalar) else f"Araç {i}"
    durum = st.session_state['arac_durumu'][i]
    
    with col:
        # Hover (Yardım) kısmında son görevi buluttan getirir
        st.button(
            label=f"{p_adi}\n{'🟢 Müsait' if durum else '🔴 Görevde'}", 
            key=f"car_{i}", 
            on_click=durum_degistir, 
            args=(i,),
            help=son_gorev_bilgisi(p_adi), 
            use_container_width=True
        )
