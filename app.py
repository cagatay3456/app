import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Yapay Zeka Öğretmeni", page_icon="🎓", layout="wide")

# Modern arayüz için özel CSS tasarımları
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h2, h3 { color: #2563EB; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 AI Yapay Zeka Dijital Öğretmeniniz")
st.write("Sorunuzun fotoğrafını yükleyin veya iPad kameranızla çekin; yapay zeka adım adım çözsün, hatalarınızı analiz edip çalışma tablonuzu hazırlasın!")

# --- GEMINI API BAĞLANTISI ---
with st.sidebar:
    st.header("🔑 Kurulum ve Ayarlar")
    api_key = st.text_input("Google Gemini API Anahtarınızı Girin:", type="password", 
                            help="ai.google.dev adresinden ücretsiz alabileceğiniz API anahtarı.")
    st.markdown("""
    <hr style='margin: 10px 0;'>
    <p style='font-size: 13px; color: #555;'>
    <b>iPad Kullanım İpucu:</b><br>
    Uygulamayı tam ekran kullanmak için Safari'de <b>Paylaş</b> butonuna basıp <b>Ana Ekrana Ekle</b> seçeneğini seçebilirsiniz.
    </p>
    """, unsafe_allow_html=True)

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    st.warning("👉 Lütfen başlamak için sol menüye Google Gemini API anahtarınızı girin.")
    st.info("💡 API anahtarınız yoksa [ai.google.dev](https://ai.google.dev) adresinden saniyeler içinde ücretsiz alabilirsiniz.")
    st.stop()

# --- HAFIZA SİMÜLASYONU ---
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = []

# --- ARAYÜZ SEKMELERİ ---
tab1, tab2 = st.tabs(["🔍 Soru Çözümü & Analiz", "📊 Konu Analiz Raporu"])

# --- SEKME 1: SORU ÇÖZÜMÜ ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 Soru Fotoğrafı")
        uploaded_file = st.file_uploader("Kamerayı açmak veya galeriden seçmek için dokunun...", type=["jpg", "jpeg", "png"])
        
        user_comment = st.text_area("Soruda yaptığın çözümü anlat veya takıldığın yeri belirt (İsteğe bağlı):", 
                                    placeholder="Örn: Ben cevabı C buldum ama anahtar B diyor. İşlem hatamı bulabilir misin?")
        
        submit_btn = st.button("🚀 Soruyu Çöz ve Analiz Et", use_container_width=True)

    with col2:
        st.subheader("🤖 Yapay Zeka Öğretmeninizin Çözümü")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Yüklenen Soru Görseli", use_container_width=True)
            
            if submit_btn:
                prompt = f"""
                Sen sabırlı, cana yakın ve son derece uzman bir lise/üniversite öğretmenisin. 
                Önündeki görseldeki soruyu ve eğer varsa kullanıcının kendi el yazısı çözümünü dikkatlice incele. 
                
                Kullanıcının ekstra notu: {user_comment if user_comment else "Belirtilmemiş."}
                
                Senden istenenler:
                1. Soruyu doğrudan şıkkı söyleyerek çözmek yerine, mantığını adım adım anlatarak ve formülleri açıklayarak çöz.
                2. Eğer kullanıcı kendi çözümünü eklemişse veya notunda hatasını soruyorsa, tam olarak hangi adımda/satırda işlem veya mantık hatası yaptığını nazikçe belirt.
                3. Çözümün en sonunda, BU SORUNUN konusunu analiz edebilmemiz için SADECE VE SADECE aşağıdaki JSON formatında bir özet ekle. JSON kod bloğu dışında bu kısımda başka karakter olmasın.
                
                JSON Formatı aynen şu şekilde olmalıdır:
                ||JSON_START||
                {{
                    "Ders": "Ders Adı",
                    "Konu": "Ana Konu ve Alt Başlık",
                    "Hata_Turu": "Kullanıcının yaptığı hata türü veya eksik olduğu anahtar nokta",
                    "Eylem_Plani": "Kullanıcının bu konuda bir daha hata yapmaması için neye çalışması gerektiği tavsiyesi"
                }}
                ||JSON_END||
                """
                
                with st.spinner("Öğretmeniniz soruyu inceleiyor..."):
                    try:
                        response = model.generate_content([prompt, image])
                        full_text = response.text
                        
                        if "||JSON_START||" in full_text and "||JSON_END||" in full_text:
                            clean_text = full_text.split("||JSON_START||")[0]
                            json_part = full_text.split("||JSON_START||")[1].split("||JSON_END||")[0].strip()
                            
                            st.markdown(clean_text)
                            
                            data_dict = json.loads(json_part)
                            st.session_state.analysis_data.append(data_dict)
                        else:
                            st.markdown(full_text)
                            
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {str(e)}")
        else:
            if submit_btn:
                st.warning("Lütfen önce bir soru fotoğrafı yükleyin.")

# --- SEKME 2: ANALİZ VE TABLO ---
with tab2:
    st.subheader("📉 Kişiselleştirilmiş Ders Çalışma Analiz Paneli")
    st.write("Yapay zekanın çözdüğü tüm sorulardan derlediği, eksiklerinize göre güncellenen dinamik çalışma tablonuz:")
    
    if st.session_state.analysis_data:
        df = pd.DataFrame(st.session_state.analysis_data)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Çalışma Planını Excel/CSV Olarak İndir",
            data=csv,
            file_name='yapay_zeka_ogretmenim_analiz.csv',
            mime='text/csv',
        )
        st.success("💡 **Öğretmen Önerisi:** Tablodaki 'Eylem Planı' maddelerini uygulayarak eksiklerinizi kapatın!")
    else:
        st.info("Henüz analiz edilmiş bir soru bulunamadı. Soruları yükledikçe burası dolacaktır.")
