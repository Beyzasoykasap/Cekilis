import streamlit as st
import csv
import os
import random
import pandas as pd

# --- AYARLAR ---
DOSYA_ADI = "katilimcilar.csv"
YONETICI_SIFRESI = "2025"  # Şifreni buradan belirle

st.set_page_config(page_title="Yılbaşı Çekilişi", page_icon="🎄")

# --- MENÜ (YAN PANEL) ---
# Pages klasörü yerine menüyü burada kendimiz oluşturuyoruz
menu_secimi = st.sidebar.radio("Menü", ["🎄 Kayıt Ekranı", "🔒 Yönetici Paneli"])

# --- 1. SAYFA: KAYIT EKRANI ---
if menu_secimi == "🎄 Kayıt Ekranı":
    st.title("🎄 Yılbaşı Çekilişine Hoş Geldin! 🎉")
    st.markdown("Aşağıdaki formu doldurarak listeye adını yazdır.")

    with st.form("kayit_formu", clear_on_submit=True):
        isim = st.text_input("Adınız Soyadınız")
        bilet_no = st.text_input("Bilet Numaranız")
        gonder_tus = st.form_submit_button("Çekilişe Katıl 🎅")

        if gonder_tus:
            if isim and bilet_no:
                dosya_yoktu = not os.path.exists(DOSYA_ADI)
                with open(DOSYA_ADI, mode="a", newline="", encoding="utf-8") as f:
                    yazici = csv.writer(f)
                    if dosya_yoktu:
                        yazici.writerow(["Isim", "BiletNo"])
                    yazici.writerow([isim, bilet_no])
                
                st.success(f"Teşekkürler {isim}, kaydın alındı! 🍀")
                st.balloons()
            else:
                st.warning("Lütfen isim ve bilet numarasını boş bırakmayın.")

# --- 2. SAYFA: YÖNETİCİ PANELİ ---
elif menu_secimi == "🔒 Yönetici Paneli":
    st.title("🔒 Yönetici Paneli")

    # Basit bir şifre kontrol mekanizması
    # Şifre daha önce girildiyse tekrar sormasın diye 'session_state' kullanıyoruz
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        sifre_girilen = st.text_input("Giriş Şifresi", type="password")
        if st.button("Giriş Yap"):
            if sifre_girilen == YONETICI_SIFRESI:
                st.session_state["admin_logged_in"] = True
                st.rerun()  # Sayfayı yenile
            else:
                st.error("Hatalı şifre!")
    else:
        # --- GİRİŞ BAŞARILI İSE BURASI GÖRÜNÜR ---
        st.success("Yönetici girişi yapıldı.")
        
        # Çıkış butonu
        if st.button("Çıkış Yap"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        st.divider()

        if os.path.exists(DOSYA_ADI):
            try:
                df = pd.read_csv(DOSYA_ADI)
                st.metric("Toplam Katılımcı", len(df))
                
                with st.expander("📋 Katılımcı Listesini Göster"):
                    st.dataframe(df, use_container_width=True)

                st.subheader("🎲 Çekiliş Yap")
                if st.button("Kazananı Belirle! 🚀", type="primary"):
                    if len(df) > 0:
                        kazanan = df.sample(1).iloc[0]
                        st.balloons()
                        st.markdown(f"## 🏆 KAZANAN: **{kazanan['Isim']}**")
                        st.info(f"Bilet No: {kazanan['BiletNo']}")
                    else:
                        st.warning("Listede kimse yok.")
            except:
                st.error("Dosya okunurken hata oluştu. Dosya boş olabilir.")
        else:
            st.warning("Henüz kimse kayıt olmadı.")