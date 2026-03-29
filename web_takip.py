import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Sözcü Takip", layout="wide")

# --- LİNKİ KONTROL ET ---
URL = "BURAYA_GOOGLE_SHEETS_LINKINI_YAPISTIR"

st.title("🚗 Sözcü Ulaştırma Takip")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # 1. VERİ OKUMA TESTİ
    st.write("🔍 Veri yolu kontrol ediliyor...")
    
    # TTL=0 ile hafızayı baypas ediyoruz
    df = conn.read(spreadsheet=URL, ttl=0)

    # YAN PANEL
    st.sidebar.header("📝 Yeni Kayıt")
    s_sofor = st.sidebar.selectbox("Şoför", ["Seçiniz...", "Celal Aslan", "Erkan", "Murat", "Mehmet"])
    s_plaka = st.sidebar.selectbox("Plaka", ["Seçiniz...", "34 ABC 123", "06 XYZ 789"])
    s_km = st.sidebar.text_input("KM")
    s_gorev = st.sidebar.text_area("Görev")

    if st.sidebar.button("KAYDET"):
        if s_sofor != "Seçiniz..." and s_gorev:
            yeni = pd.DataFrame([{
                "tarih": datetime.now().strftime("%d.%m.%Y"),
                "saat": datetime.now().strftime("%H:%M"),
                "sofor": s_sofor,
                "plaka": s_plaka,
                "km": s_km,
                "gorev": s_gorev
            }])
            
            # Veriyi gönder
            try:
                # Eğer mevcut veri boşsa sadece yeniyi gönder
                if df is None or df.empty:
                    conn.update(spreadsheet=URL, data=yeni)
                else:
                    son_df = pd.concat([df, yeni], ignore_index=True)
                    conn.update(spreadsheet=URL, data=son_df)
                
                st.sidebar.success("Kayıt Gönderildi!")
                st.rerun()
            except Exception as e:
                if "200" in str(e):
                    st.sidebar.success("✅ Başarılı (200)")
                    st.rerun()
                else:
                    st.sidebar.error(f"Yazma Hatası: {e}")

    # 2. VERİYİ GÖSTERME (ZORLAYICI MOD)
    st.subheader("📋 Hareket Listesi")
    
    if df is not None and not df.empty:
        st.dataframe(df.dropna(how='all'), use_container_width=True)
    else:
        st.warning("⚠️ Excel'e ulaşıldı ama tablo boş görünüyor.")
        st.info("İpucu: Excel dosyasının ilk satırında 'tarih, saat, sofor, plaka, km, gorev' yazdığından emin olun.")

except Exception as e:
    st.error("🚨 KRİTİK BAĞLANTI HATASI")
    st.write(f"Hata Kodu: {e}")
