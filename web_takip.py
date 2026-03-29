import streamlit as st
from supabase import create_client, Client

URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h" 
supabase: Client = create_client(URL, KEY)

st.title("Sözcü Ulaştırma - Tablo Bulma Modu")

try:
    # Bu komut veritabanındaki tüm tablo isimlerini listeler
    res = supabase.rpc('get_tables').execute() 
    st.write("Veritabanında Bulunan Tablolar:", res.data)
except:
    # Eğer yukarıdaki çalışmazsa şunu dene (Manuel kontrol)
    st.warning("Tablo listesi çekilemedi. Lütfen Supabase'deki tablo ismini aşağıya ELİNİZLE yazıp deneyin.")
    tablo_adi = st.text_input("Supabase'deki tablo adını buraya yazın (Örn: kisiler)", "kisiler")
    
    if st.button("Tabloyu Sorgula"):
        try:
            test = supabase.table(tablo_adi).select("*").execute()
            st.success(f"BULDUM! {tablo_adi} tablosu çalışıyor. Veriler: {test.data}")
        except Exception as e:
            st.error(f"Hata: {e}")
