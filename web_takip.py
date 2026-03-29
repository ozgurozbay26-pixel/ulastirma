import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time
import uuid

st.set_page_config(page_title="Sözcü Takip Pro", layout="wide")

# --- 1. BAĞLANTI ---
@st.cache_resource
def gsheet_baglan():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    url = "https://docs.google.com/spreadsheets/d/1O4jyJR4cGARY4ScACpL1GDD2GhwZ9lSBUIaaSlI9TCA/edit?usp=sharing"
    return client.open_by_url(url)

try:
    doc = gsheet_baglan()
    sheet_kayitlar = doc.get_worksheet(0)
    
    def liste_getir(sayfa_adi):
        try:
            return sorted(doc.worksheet(sayfa_adi).col_values(1)[1:])
        except: return []

    sofor_listesi = liste_getir("soforler")
    arac_listesi = liste_getir("araclar")
    durum_listesi = liste_getir("durum")
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}"); st.stop()

# --- 2. VERİ YÜKLEME ---
rows = sheet_kayitlar.get_all_records()
df = pd.DataFrame(rows)

# --- 3. YAN PANEL (YENİ KAYIT) ---
st.sidebar.header("📝 Yeni Hareket")
with st.sidebar.form("yeni_kayit_form", clear_on_submit=True):
    s_tarih = st.date_input("Tarih", datetime.now())
    s_saat = st.time_input("Saat", time(12, 0))
    s_sofor = st.selectbox("Şoför", ["Seçiniz..."] + sofor_listesi)
    s_plaka = st.selectbox("Plaka", ["Seçiniz..."] + arac_listesi)
    s_km = st.text_input("KM")
    s_durum = st.selectbox("Durum", ["Seçiniz..."] + durum_listesi)
    s_gorev = st.text_area("Görev")
    submit = st.form_submit_button("KAYDET")

if submit:
    if s_sofor != "Seçiniz..." and s_plaka != "Seçiniz...":
        yeni_id = str(uuid.uuid4())[:8] # Kısa benzersiz ID
        yeni_satir = [yeni_id, s_tarih.strftime("%d.%m.%Y"), s_saat.strftime("%H:%M"), s_sofor, s_plaka, s_km, s_gorev, s_durum]
        sheet_kayitlar.append_row(yeni_satir)
        st.sidebar.success("Kayıt Eklendi!")
        st.rerun()

# --- 4. ANA EKRAN & FİLTRELER ---
st.title("🚗 Sözcü Ulaştırma Hareket Arşivi")

if not df.empty:
    st.markdown("### 🔍 Filtreleme ve Yönetim")
    # Filtreler (Kodun önceki versiyonundaki gibi...)
    c1, c2, c3 = st.columns(3)
    with c1: f_sofor = st.multiselect("Şoför", df["sofor"].unique())
    with c2: f_plaka = st.multiselect("Plaka", df["plaka"].unique())
    with c3: f_durum = st.multiselect("Durum", df["durum"].unique())

    f_df = df.copy()
    if f_sofor: f_df = f_df[f_df["sofor"].isin(f_sofor)]
    if f_plaka: f_df = f_df[f_df["plaka"].isin(f_plaka)]
    if f_durum: f_df = f_df[f_df["durum"].isin(f_durum)]

    st.dataframe(f_df, use_container_width=True, hide_index=True)

    # --- SİLME VE DÜZENLEME ALANI ---
    st.markdown("---")
    st.subheader("🛠️ Kayıt Düzenle veya Sil")
    
    secilen_id = st.selectbox("İşlem yapılacak kaydın ID'sini seçin:", ["Seçiniz..."] + f_df["id"].tolist())
    
    if secilen_id != "Seçiniz...":
        kayit_index = df[df['id'] == secilen_id].index[0] + 2 # Excel satır numarası (+2 çünkü başlık ve 0-index)
        eski_veri = df[df['id'] == secilen_id].iloc[0]

        col_edit, col_del = st.columns(2)
        
        with col_edit:
            st.write("📝 **Bilgileri Güncelle**")
            yeni_km = st.text_input("Yeni KM", value=str(eski_veri['km']))
            yeni_gorev = st.text_area("Yeni Görev", value=str(eski_veri['gorev']))
            if st.button("GÜNCELLE"):
                sheet_kayitlar.update_cell(kayit_index, 6, yeni_km) # KM sütunu
                sheet_kayitlar.update_cell(kayit_index, 7, yeni_gorev) # Görev sütunu
                st.success("Güncellendi!")
                st.rerun()

        with col_del:
            st.write("🗑️ **Kaydı Sil**")
            st.warning("Bu işlem geri alınamaz!")
            if st.button("KAYDI SİL"):
                sheet_kayitlar.delete_rows(int(kayit_index))
                st.success("Kayıt Silindi!")
                st.rerun()
else:
    st.info("Kayıt bulunamadı.")
