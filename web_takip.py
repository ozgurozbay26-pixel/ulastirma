import streamlit as st
from supabase import create_client

URL = "https://rmzfbgaimyuacpovpxm.supabase.co"
KEY = "sb_publishable_AIPebE5Fs4zSKM36R9VUMQ_yuS8Ih-h"

supabase = create_client(URL, KEY)

st.title("DEBUG")

try:
    res = supabase.table("kisiler").select("*").execute()
    
    st.write("FULL RESPONSE:", res)
    st.write("DATA:", res.data)

except Exception as e:
    st.error(f"HATA: {e}")
