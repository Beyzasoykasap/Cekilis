import streamlit as st
import pandas as pd
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from streamlit_lottie import st_lottie

# --- AYARLAR ---

SHEET_ADI = "YilbasiCekilis2025" 
YONETICI_SIFRESI = "2025"

st.set_page_config(page_title="2025 Yılbaşı Çekilişi", page_icon="🎄", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; padding: 10px; border-radius: 10px; }
    .stButton>button:hover { background-color: #ff0000; border-color: white; box-shadow: 0px 0px 10px white; }
    h1 { text-align: center; color: #d63031; }
    </style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def sheet_baglan():
    try:
        # Secrets'tan bilgileri çek
        secrets = st.secrets["gcp_service_account"]
        
        # Yetkilendirme ayarları
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(secrets, scopes=scope)
        client = gspread.authorize(creds)
        
        # Tabloyu aç
        sheet = client.open(SHEET_ADI).sheet1
        return sheet
    except Exception as e:
        st.error(f"Google Sheets bağlantı hatası: {e}")
        return None

def verileri_cek():
    sheet = sheet_baglan()
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

def veri_ekle(isim, bilet_no):
    sheet = sheet_baglan()
    if sheet:
        sheet.append_row([isim, str(bilet_no)])

def veri_sil(bilet_no_sil):
    sheet = sheet_baglan()
    if sheet:
        # Tüm bilet numaralarını çekip hangisi olduğunu bulmamız lazım
        tum_biletler = sheet.col_values(2) 
        
        try:
            row_index = tum_biletler.index(str(bilet_no_sil)) + 1
            sheet.delete_rows(row_index)
            return True
        except ValueError:
            return False

# --- ANİMASYON ---
def lottie_yukle(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

menu_secimi = st.sidebar.radio("Menü", ["🎄 Kayıt Ekranı", "🔒 Yönetici Paneli"])

# ==========================================
# 🎄 1. SAYFA: KAYIT EKRANI
# ==========================================
if menu_secimi == "🎄 Kayıt Ekranı":
    # Animasyon
    lottie_url = "https://assets10.lottiefiles.com/packages/lf20_tij4c4.json"
    lottie_json = lottie_yukle(lottie_url)
    if lottie_json: st_lottie(lottie_json, height=200)

    st.title("🎅 Hoş Geldiniz! 🎁")
    
    with st.form("kayit_formu", clear_on_submit=True):
        isim = st.text_input("👤 Adınız Soyadınız")
        bilet_no = st.text_input("🎟️ Bilet Numaranız")
        gonder = st.form_submit_button("❄️ KAYDET ❄️")
        
        if gonder:
            if isim and bilet_no:
                df = verileri_cek()
                
                # Kontrol: Bilet var mı?
                bilet_var = False
                if not df.empty:
                    # Tipleri string yapıp kontrol et
                    mevcut_biletler = df["BiletNo"].astype(str).tolist()
                    if str(bilet_no) in mevcut_biletler:
                        bilet_var = True
                
                if bilet_var:
                    st.warning(f"⚠️ {bilet_no} zaten alınmış!")
                else:
                    veri_ekle(isim, bilet_no)
                    st.snow()
                    st.success("Kaydınız Google Sheets'e işlendi! ✅")
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("Eksik bilgi girdiniz.")

# ==========================================
# 🔒 2. SAYFA: YÖNETİCİ PANELİ
# ==========================================
elif menu_secimi == "🔒 Yönetici Paneli":
    st.title("🔒 Yönetici Paneli")
    
    if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if sifre == YONETICI_SIFRESI:
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Yanlış şifre")
    else:
        if st.button("Çıkış"):
            st.session_state.admin_logged_in = False
            st.rerun()
        
        st.divider()
        df = verileri_cek()
        
        if not df.empty:
            df["BiletNo"] = df["BiletNo"].astype(str)
            st.metric("Katılımcı Sayısı", len(df))
            st.dataframe(df, use_container_width=True)
            
            # SİLME İŞLEMİ
            st.subheader("🗑️ Kayıt Sil")
            silinecek = st.selectbox("Seç:", df["BiletNo"] + " - " + df["Isim"])
            if st.button("🚫 SİL"):
                bilet_sil = silinecek.split(" - ")[0]
                if veri_sil(bilet_sil):
                    st.success("Silindi!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Silinemedi.")
            
            st.divider()
            
            # ÇEKİLİŞ
            if st.button("🚀 ÇEKİLİŞ YAP", type="primary"):
                if len(df) > 0:
                    bar = st.progress(0, "Karıştırılıyor...")
                    for i in range(100):
                        time.sleep(0.01)
                        bar.progress(i+1)
                    bar.empty()
                    
                    if len(df) >= 2:
                        kazananlar = df.sample(2)
                        asil = kazananlar.iloc[0]
                        yedek = kazananlar.iloc[1]
                        st.balloons()
                        st.success(f"🏆 ASIL: {asil['Isim']} ({asil['BiletNo']})")
                        st.info(f"✨ YEDEK: {yedek['Isim']} ({yedek['BiletNo']})")
                    else:
                        k = df.sample(1).iloc[0]
                        st.balloons()
                        st.success(f"🏆 KAZANAN: {k['Isim']} ({k['BiletNo']})")
        else:
            st.warning("Liste boş veya okunamadı.")
