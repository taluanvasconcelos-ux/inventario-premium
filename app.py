import streamlit as st
import requests
import csv
import gspread
import json
import streamlit.components.v1 as components
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(
    page_title="Inventário Extrajudicial | Vasconcelos Maia",
    layout="centered",
    page_icon="⚖️"
)

# -----------------------------
# CSS PREMIUM ATUALIZADO
# -----------------------------
st.markdown("""
<style>
    .main-title { text-align: center; font-size: 38px; font-weight: 700; color: #1a1a1a; margin-bottom: 0px; }
    .subtitle { text-align: center; font-size: 18px; color: #666; margin-bottom: 30px; }
    
    .cta-container { 
        display: flex; justify-content: center; gap: 15px; 
        margin: 20px 0; flex-wrap: wrap; 
    }
    
    .btn-calendly {
        background-color: #0A2540; color: white !important; padding: 12px 24px;
        border-radius: 8px; text-decoration: none; font-weight: 600;
    }
    
    .btn-whatsapp {
        background-color: #25D366; color: white !important; padding: 12px 24px;
        border-radius: 8px; text-decoration: none; font-weight: 600;
    }

    .section-box {
        background-color: #ffffff; padding: 30px; border-radius: 15px;
        border: 1px solid #eee; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO E CABEÇALHO
# -----------------------------
col1, col2, col3 = st.columns([1,1.5,1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown('<h1 class="main-title">Inventário em Cartório</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análise rápida e segura para o seu caso.</p>', unsafe_allow_html=True)

# -----------------------------
# INTEGRAÇÕES (SECRETAS)
# -----------------------------
def enviar_telegram(msg):
    token = st.secrets["TELEGRAM_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
    except: pass

def salvar_google(dados):
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Leads Inventário").sheet1
        sheet.append_row(dados)
    except: pass

# -----------------------------
# FORMULÁRIO
# -----------------------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
with st.form("meu_form"):
    nome = st.text_input("Nome completo")
    whatsapp = st.text_input("WhatsApp (com DDD)")
    
    c1, c2 = st.columns(2)
    with c1:
        herdeiro = st.radio("Herdeiro incapaz?", ["Não", "Sim"])
        consenso = st.radio("Todos de acordo?", ["Sim", "Não"])
    with c2:
        bens = st.radio("Existem bens?", ["Sim", "Não"])
        testamento = st.radio("Existe testamento?", ["Não", "Sim"])
    
    lgpd = st.checkbox("Autorizo o tratamento dos meus dados de acordo com a LGPD, e o contato profissional.")
    submit = st.form_submit_button("ANALISAR AGORA")

if submit:
    if not lgpd or not nome or not whatsapp:
        st.error("Preencha os campos obrigatórios.")
    else:
        # Lógica Simples
        if herdeiro == "Sim" or consenso == "Não":
            res = "Judicial"
            st.warning("### Necessário Inventário Judicial")
        else:
            res = "Extrajudicial"
            st.success("### Possível Inventário em Cartório!")
            st.balloons()
        
        # Salvar Dados
        salvar_google([nome, whatsapp, res, datetime.now().strftime("%d/%m/%Y %H:%M")])
        enviar_telegram(f"🚀 *Novo Lead:* {nome}\n*Whats:* {whatsapp}\n*Resultado:* {res}")

        st.markdown("---")
        st.markdown("### Próximos Passos:")
        
        # WIDGET DO CALENDLY EMOLDURADO
        components.html(
            f"""
            <div class="calendly-inline-widget" data-url="https://calendly.com/SEU-LINK" style="min-width:320px;height:630px;"></div>
            <script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
            """,
            height=650,
        )

st.markdown('</div>', unsafe_allow_html=True)
# -----------------------------
# FIM DO FORMULÁRIO (FECHANDO A DIV)
# -----------------------------
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# SEÇÃO DE AGENDAMENTO (FORA DO FORMULÁRIO)
# -----------------------------
st.markdown("---")
st.markdown("<h3 style='text-align:center;'>Agende sua Consultoria Estratégica</h3>", unsafe_allow_html=True)

# Tenta carregar o Widget do Calendly
# IMPORTANTE: Troque 'SEU-LINK' pelo seu link real do Calendly
calendly_url = "https://calendly.com/SEU-LINK" 

components.html(
    f"""
    <div class="calendly-inline-widget" data-url="{calendly_url}" style="min-width:320px;height:630px;"></div>
    <script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
    """,
    height=650,
)

# -----------------------------
# BOTÕES DE RODAPÉ (SEMPRE VISÍVEIS)
# -----------------------------
st.markdown("""<h4 style='text-align:center; margin-top:30px;'>Fale diretamente conosco:</h4>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="cta-container">
    <a href="{calendly_url}" target="_blank" class="btn-calendly">🗓️ ABRIR CALENDÁRIO COMPLETO</a>
    <a href="https://wa.me/5583996498366?text=Olá, vim pelo site e gostaria de uma análise de inventário." 
       target="_blank" class="btn-whatsapp">💬 CHAMAR NO WHATSAPP</a>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# RODAPÉ FINAL
# -----------------------------
st.markdown(f"""
<div class="footer">
    <hr>
    © {datetime.now().year} Vasconcelos Maia | Soluções Jurídicas<br>
    | Atendimento em todo o Brasil
</div>
""", unsafe_allow_html=True)
