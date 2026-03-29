import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

# --- 1. DOSYA YOLU VE AYARLAR ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_yolu = os.path.join(BASE_DIR, 'kisiler.db')

# Sayfa Ayarları (Web tarayıcısı sekmesinde görünür)
st.set_page_config(page_title="Sözcü Ulaştırma Web", layout="wide")

# --- 2. SESSION STATE (Oturum Hafızası) AYARLARI ---
# Araçların Müsait/Dolu durumunu ve plakalarını aklında tutması için hafıza oluşturuyoruz
if 'arac_durumu' not in st.session_state:
    st.session_state['arac_durumu'] = {i: True for i in range(1, 9)} # True = Müsait, False = Görevde

# Tıklayınca durumu tersine çeviren fonksiyon (Müsait <-> Görevde)
def durum_degistir(arac_id):
    st.session_state['arac_durumu'][arac_id] = not st.session_state['arac_durumu'][arac_id]

# --- 3. VERİTABANI FONKSİYONLARI ---
def veritabani_hazirla():
    # Eğer tablo yoksa hata vermemesi için otomatik oluştururuz
    conn = sqlite3.connect(db_yolu)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            sofor TEXT NOT NULL,
            plaka TEXT,
            saat TEXT,
            km TEXT,
            gorev TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Sayfa her yüklendiğinde veritabanı hazır mı diye kontrol eder
veritabani_hazirla()

def verileri_yukle():
    try:
        # Burada direkt yukarıda tanımladığımız 'db_yolu'nu kullanıyoruz
        conn = sqlite3.connect(db_yolu)
        # Verileri id'ye göre tersten sıralayarak çekeriz (En yeni en üstte)
        df = pd.read_sql_query("SELECT * FROM kayitlar ORDER BY id DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def listeleri_getir():
    # Açılır menüler (ComboBox) için şoför ve plaka listelerini hazırlar
    soforler = ["Seçiniz..."]
    plakalar = ["Seçiniz..."]
    try:
        conn = sqlite3.connect(db_yolu)
        c = conn.cursor()
        
        # 'kisiler' tablosundan şoförleri çek (Eğer bu tablo veritabanında varsa)
        c.execute("SELECT ad_soyad FROM kisiler ORDER BY ad_soyad ASC")
        soforler += [row[0] for row in c.fetchall()]
        
        # 'plaka' tablosundan plakaları çek (Eğer bu tablo veritabanında varsa)
        c.execute("SELECT plaka_no FROM plaka ORDER BY plaka_no ASC")
        plakalar += [row[0] for row in c.fetchall()]
        
        conn.close()
    except:
        # Eğer tablolar henüz yoksa hata vermemesi için varsayılan bırakır
        pass
    return soforler, plakalar

# YENİ: Sadece seçili plakaya ait son görevi getiren fonksiyon (Tooltip için)
def araca_ait_son_gorevi_getir(secili_plaka):
    try:
        conn = sqlite3.connect(db_yolu)
        c = conn.cursor()
        # Plakaya göre filtreleyip en son kaydı (id DESC) getiriyoruz
        c.execute("SELECT sofor, gorev FROM kayitlar WHERE plaka=? ORDER BY id DESC LIMIT 1", (secili_plaka,))
        son_kayit = c.fetchone()
        conn.close()
        
        if son_kayit:
            return f"Şoför: {son_kayit[0]}\nSon Görev: {son_kayit[1]}"
        return "Bu araca ait henüz görev girilmemiş."
    except:
        return "Bilgi alınamadı."

# Listeleri bir kez sayfa başında yükleriz
sofor_listesi, plaka_listesi = listeleri_getir()

# --- 4. SOL PANEL (YENİ KAYIT FORMU) ---
st.sidebar.header("📝 Yeni Görev Kaydı")

# COMBOBOX'LAR (st.selectbox)
s_sofor = st.sidebar.selectbox("Şoför Seçin (*)", sofor_listesi)
s_plaka = st.sidebar.selectbox("Plaka Seçin", plaka_listesi)

# Diğer Girişler
s_saat = st.sidebar.time_input("Saat Seçin")
s_km = st.sidebar.text_input("Araç KM", placeholder="Örn: 154000")
s_gorev = st.sidebar.text_area("Geniş Görev (*)")

# Kaydet Butonu
kaydet = st.sidebar.button("Kaydet", use_container_width=True, type="primary")

if kaydet:
    if s_sofor != "Seçiniz..." and s_gorev.strip():
        try:
            conn = sqlite3.connect(db_yolu)
            c = conn.cursor()
            tarih_str = date.today().strftime("%d.%m.%Y")
            saat_str = s_saat.strftime("%H:%M")
            
            c.execute("INSERT INTO kayitlar (tarih, sofor, plaka, saat, km, gorev) VALUES (?, ?, ?, ?, ?, ?)",
                      (tarih_str, s_sofor, s_plaka, saat_str, s_km, s_gorev))
            conn.commit()
            conn.close()
            st.sidebar.success(f"Kayıt Başarılı: {s_sofor}")
            
            # Sayfayı yenileyerek yeni kaydın hemen tabloda görünmesini sağlarız
            try: st.rerun()
            except: st.experimental_rerun()
            
        except Exception as e:
            st.sidebar.error(f"Hata oluştu: {e}")
    else:
        st.sidebar.warning("Lütfen şoför seçin ve görev detayını yazın!")

# --- 5. ANA PANEL (FİLTRELER VE TABLO) ---
st.title("🚗 Sözcü Ulaştırma Takip Paneli")

# Verileri Çek
df = verileri_yukle()

# FİLTRELEME BÖLÜMÜ
st.subheader("🔍 Filtreleme")
f_col1, f_col2, f_col3 = st.columns(3)

if not df.empty:
    with f_col1:
        f_sofor = st.selectbox("Şoföre Göre", ["Tümü"] + list(df['sofor'].unique()))
    with f_col2:
        f_plaka = st.selectbox("Plakaya Göre", ["Tümü"] + list(df['plaka'].unique()))
    with f_col3:
        f_tarih = st.selectbox("Tarihe Göre", ["Tümü"] + list(df['tarih'].unique()))

    # Seçilen Filtreleri Dataframe'e Uygula
    if f_sofor != "Tümü":
        df = df[df['sofor'] == f_sofor]
    if f_plaka != "Tümü":
        df = df[df['plaka'] == f_plaka]
    if f_tarih != "Tümü":
        df = df[df['tarih'] == f_tarih]

st.divider()

# TABLO BAŞLIĞI VE EXCEL İNDİRME YAN YANA
col_baslik, col_indir = st.columns([3, 1])
with col_baslik:
    st.subheader(f"📋 Kayıtlar (Toplam: {len(df)})")
with col_indir:
    if not df.empty:
        # utf-8-sig ile Türkçe karakter desteği sağlanır
        csv_verisi = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Excel İndir",
            data=csv_verisi,
            file_name=f'Rapor_{date.today().strftime("%d_%m_%Y")}.csv',
            mime='text/csv',
            use_container_width=True
        )

# TABLO GÖSTERİMİ VE SİLME
if not df.empty:
    # use_container_width=True ile tabloyu tüm genişliğe yayarız
    # hide_index=True ile baştaki gereksiz sıra numaralarını gizliyoruz
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # SİLME BÖLÜMÜ
    st.divider()
    st.subheader("🗑️ Kayıt Silme")
    s_col1, s_col2 = st.columns([1, 4])
    with s_col1:
        # Sadece o an filtrelenmiş tabloda görünen ID'leri silmeye izin ver
        silinecek_id = st.selectbox("Silinecek Kayıt ID'sini Seçin", df['id'].tolist())
    with s_col2:
        st.write("") # Butonu hizalamak için boşluk
        st.write("") 
        if st.button("Seçili Kaydı Sil", type="secondary"):
            try:
                conn = sqlite3.connect(db_yolu)
                c = conn.cursor()
                c.execute("DELETE FROM kayitlar WHERE id=?", (silinecek_id,))
                conn.commit()
                conn.close()
                st.warning(f"ID {silinecek_id} başarıyla silindi!")
                try: st.rerun()
                except: st.experimental_rerun()
            except Exception as e:
                st.error(f"Silme işlemi başarısız: {e}")
else:
    st.info("Bu filtrelere uygun veya gösterilecek herhangi bir kayıt bulunamadı.")

# ==========================================
# --- 6. ARAÇ DURUM PANELİ (Küçültülmüş ve Gerçek Plakalı) ---
# ==========================================
st.divider()
st.subheader("🚙 Araç Durum Paneli")
st.caption("Araçların üzerine tıklayarak Müsait/Görevde durumlarını değiştirebilir, farenizi üzerinde bekleterek o plakaya ait son görevi görebilirsiniz.")

# 8 araç için 2 satır, 4 sütunlu ızgara
cols_ust = st.columns(4)
cols_alt = st.columns(4)
tum_sutunlar = cols_ust + cols_alt

# Sadece gerçek plakaları al (İlk baştaki "Seçiniz..." ibaresini atlıyoruz)
gercek_plakalar = plaka_listesi[1:] if len(plaka_listesi) > 1 else []

# 8 Araç Slotunu dolduruyoruz
for i in range(1, 9):
    col = tum_sutunlar[i - 1]
    
    # 8 Slota sığdıracak şekilde plakaları yerleştir (Plaka yetmezse "Araç X" yazar)
    if (i - 1) < len(gercek_plakalar):
        gosterilecek_plaka = gercek_plakalar[i - 1]
    else:
        gosterilecek_plaka = f"Araç {i}"

    musait_mi = st.session_state['arac_durumu'][i]
    durum_yazisi = "🟢 Müsait" if musait_mi else "🔴 Görevde"
    
    # YENİ: Tooltip bilgisini seçili plakaya özel getiriyoruz (Sadece 'Görevde' ise)
    hover_bilgisi = araca_ait_son_gorevi_getir(gosterilecek_plaka) if not musait_mi else "Araç şu an müsait."
    
    with col:
        # Resmi klasörde bulursa gösterir, bulamazsa emoji gösterir
        resim_yolu = os.path.join(BASE_DIR, "car.png")
        if os.path.exists(resim_yolu):
            # *** DEĞİŞİKLİK BURADA: 'width=100' ekleyerek resimleri küçülttük ***
            # Önceki kodda: st.image(resim_yolu, use_container_width=True) idi.
            st.image(resim_yolu, width=100)
        else:
            # Resim yoksa emoji göster, onu da küçültelim (style tagı ile)
            st.markdown("<h3 style='text-align: center;'>🚗</h3>", unsafe_allow_html=True)
            
        # Resmin hemen altına tıklanabilir butonu koy
        # help="..." kısmı, farenin ucuyla butonun üstünde durunca açılan kutucuktur (Tooltip)!
        st.button(
            label=f"{gosterilecek_plaka} \n {durum_yazisi}", # Buton isminde direkt plaka yazar
            key=f"arac_btn_{i}",
            help=hover_bilgisi,
            on_click=durum_degistir,
            args=(i,), # Hangi araca tıklandığını fonksiyona gönderir
            use_container_width=True
        )