import streamlit as st
import csv
import os
import random
import pandas as pd
import time

# --- AYARLAR ---
DOSYA_ADI = "katilimcilar.csv"
YONETICI_SIFRESI = "2025"  # Şifreni buradan belirle

st.set_page_config(
    page_title="2025 Yılbaşı Çekilişi", 
    page_icon="🎄",
    layout="centered"
)

# --- CSS İLE GÜZELLEŞTİRME ---
st.markdown("""
    <style>
    /* Butonu kırmızı ve büyük yapalım */
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-size: 20px;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff0000;
        border-color: white;
        box-shadow: 0px 0px 10px white;
    }
    /* Başlık stili */
    h1 {
        text-align: center; 
        color: #d63031;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÜ ---
menu_secimi = st.sidebar.radio("Menü", ["🎄 Kayıt Ekranı", "🔒 Yönetici Paneli"])

# ==========================================
# 🎄 1. SAYFA: KAYIT EKRANI
# ==========================================
if menu_secimi == "🎄 Kayıt Ekranı":
    
    st.title("🎅 Hoş Geldiniz! 🎁")
    st.markdown("<h3 style='text-align: center; color: gray;'>Yılbaşı çekilişi için kaydınızı oluşturun.</h3>", unsafe_allow_html=True)
    st.write("") 
    
    with st.container():
        with st.form("kayit_formu", clear_on_submit=True):
            isim = st.text_input("👤 Adınız Soyadınız", placeholder="Örn: Beyza Soykasap")
            # --- DÜZELTİLEN SATIR BURASI ---
            bilet_no = st.text_input("🎟️ Bilet Numaranız", placeholder="Örn: 17")
            
            st.write("")
            gonder_tus = st.form_submit_button("❄️ KAYDET ❄️")

            if gonder_tus:
                if isim and bilet_no:
                    # --- KONTROL MEKANİZMASI ---
                    bilet_zaten_var = False
                    
                    if os.path.exists(DOSYA_ADI):
                        try:
                            mevcut_df = pd.read_csv(DOSYA_ADI)
                            # Bilet numaralarını string formatına çevirip listeye alıyoruz
                            alinmis_biletler = mevcut_df["BiletNo"].astype(str).tolist()
                            if bilet_no in alinmis_biletler:
                                bilet_zaten_var = True
                        except:
                            pass
                    
                    if bilet_zaten_var:
                        st.warning(f"⚠️ {bilet_no} numaralı bilet daha önce alınmış! Lütfen başka bir numara girin.")
                    else:
                        dosya_yoktu = not os.path.exists(DOSYA_ADI)
                        with open(DOSYA_ADI, mode="a", newline="", encoding="utf-8") as f:
                            yazici = csv.writer(f)
                            if dosya_yoktu:
                                yazici.writerow(["Isim", "BiletNo"])
                            yazici.writerow([isim, bilet_no])
                        
                        st.snow()
                        st.success(f"Harika! {isim}, kaydın alındı. Bol şans! 🍀")
                        time.sleep(7)
                        try:
                            st.rerun()
                        except AttributeError:
                            # Eski streamlit sürümleri için alternatif
                            st.experimental_rerun()
                else:
                    st.error("Lütfen isim ve bilet numarasını eksiksiz girin.")

# ==========================================
# 🔒 2. SAYFA: YÖNETİCİ PANELİ
# ==========================================
elif menu_secimi == "🔒 Yönetici Paneli":
    st.title("🔒 Yönetici Paneli")

    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        sifre_girilen = st.text_input("Giriş Şifresi", type="password")
        if st.button("Giriş Yap"):
            if sifre_girilen == YONETICI_SIFRESI:
                st.session_state["admin_logged_in"] = True
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error("Hatalı şifre!")
    else:
        # Yönetici İçeriği
        st.success("Yönetici girişi yapıldı.")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Çıkış Yap"):
                st.session_state["admin_logged_in"] = False
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

        st.divider()

        if os.path.exists(DOSYA_ADI):
            try:
                df = pd.read_csv(DOSYA_ADI)
                # Veri tipi güvenliği (Her şeyi string yapalım)
                df["BiletNo"] = df["BiletNo"].astype(str)
                df["Isim"] = df["Isim"].astype(str)
                
                st.metric("Toplam Katılımcı", len(df))
                
                with st.expander("📋 Katılımcı Listesini Gör"):
                    st.dataframe(df, use_container_width=True)

                # --- SİLME BÖLÜMÜ ---
                st.write("")
                st.subheader("🗑️ Kayıt Sil")
                if len(df) > 0:
                    # Silme listesi oluştur
                    silinecek_secenekler = df["BiletNo"] + " - " + df["Isim"]
                    secilen_kisi = st.selectbox("Silinecek Kişiyi Seç:", silinecek_secenekler)
                    
                    if st.button("🚫 SEÇİLİ KAYDI SİL"):
                        # Seçilen string'den sadece bilet numarasını al
                        silinecek_bilet_no = secilen_kisi.split(" - ")[0]
                        
                        # Filtrele ve kaydet
                        yeni_df = df[df["BiletNo"] != silinecek_bilet_no]
                        yeni_df.to_csv(DOSYA_ADI, index=False)
                        
                        st.success(f"{secilen_kisi} başarıyla silindi!")
                        time.sleep(1)
                        try:
                            st.rerun()
                        except AttributeError:
                            st.experimental_rerun()
                else:
                    st.info("Silinecek kayıt yok.")
                st.divider()

                # --- ÇEKİLİŞ BÖLÜMÜ ---
                st.subheader("🎲 Büyük Çekiliş")
                st.write("Herkes hazırsa butona bas!")
                
                if st.button("🚀 KAZANANI BELİRLE", type="primary"):
                    if len(df) > 0:
                        progress_text = "Torba karıştırılıyor... 🥁"
                        my_bar = st.progress(0, text=progress_text)
                        for percent_complete in range(100):
                            time.sleep(0.01)
                            my_bar.progress(percent_complete + 1, text=progress_text)
                        my_bar.empty()
                        
                        kazanan = df.sample(1).iloc[0]
                        st.balloons()
                        st.markdown(f"<h1 style='color: green; text-align: center;'>🏆 {kazanan['Isim']} 🏆</h1>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: center;'>Bilet No: {kazanan['BiletNo']}</h3>", unsafe_allow_html=True)
                    else:
                        st.warning("Listede kimse yok.")
            except Exception as e:
                st.error(f"Dosya okunurken hata oluştu: {e}")
        else:
            st.warning("Henüz kimse kayıt olmadı.")
