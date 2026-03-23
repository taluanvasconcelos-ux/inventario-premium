import streamlit as st
import requests
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
# CSS PREMIUM (DESIGN)
# -----------------------------
st.markdown("""
<style>
    /* Remove espaços vazios no topo e laterais */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 50rem !important;
    }
    
    /* Remove a barra branca/espaço em cima do formulário */
    [data-testid="stForm"] {
        margin-top: -20px !important;
        padding: 20px !important;
    }

    /* Ajusta o título para não empurrar o form para baixo */
    .main-title { 
        text-align: center; 
        font-size: 32px; 
        font-weight: 700; 
        margin-bottom: 0px !important; 
    }
    
    .subtitle { 
        text-align: center; 
        font-size: 16px; 
        color: #666; 
        margin-bottom: 10px !important; 
    }

    /* Esconde o cabeçalho padrão do Streamlit para ganhar espaço */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO E CABEÇALHO
# -----------------------------
# 1. Logo
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    st.image("logo.png", use_container_width=True)

# 2. Títulos (fora de qualquer container ou form)
st.markdown('<h1 class="main-title">Inventário Extrajudicial</h1>', unsafe_allow_html=True)


# -----------------------------
# INTEGRAÇÕES (SAFE)
# -----------------------------
def enviar_telegram(msg):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
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
# FORMULÁRIO COM CHECKBOXES DESATIVADOS (INDEX=NONE)
# -----------------------------
with st.form("form_analise"):
    st.subheader("📍 Pré-Análise do Caso")
    
    nome = st.text_input("Nome completo")
    whatsapp = st.text_input("WhatsApp (com DDD)")
    email = st.text_input("E-mail profissional") # <-- CAMPO NOVO
    
    st.write("**Responda abaixo (seleção obrigatória):**")
    
    c1, c2 = st.columns(2)
    with c1:
        herdeiro = st.radio("Existe herdeiro incapaz (menor)?", ["Não", "Sim"], index=None)
        consenso = st.radio("Todos estão de acordo com a divisão?", ["Sim", "Não"], index=None)
    with c2:
        bens = st.radio("Existem bens a partilhar?", ["Sim", "Não"], index=None)
        testamento = st.radio("Existe testamento?", ["Não", "Sim", "Não sei"], index=None)
    
    lgpd = st.checkbox("Autorizo o contato para fins de análise jurídica.")
    submit = st.form_submit_button("ANALISAR MEU CASO AGORA")

# -----------------------------
# LÓGICA DE PROCESSAMENTO
# -----------------------------
if submit:
    # Adicionámos o 'email' na verificação de campos vazios
    if None in [herdeiro, consenso, bens, testamento] or not nome or not whatsapp or not email:
        st.error("⚠️ Por favor, preencha todos os campos (incluindo o e-mail) antes de prosseguir.")
    elif not lgpd:
        st.error("⚠️ Você precisa autorizar o contato (LGPD) para ver o resultado.")
    else:
        # Lógica de classificação (mantém-se a mesma)
        if herdeiro == "Sim" or consenso == "Não":
            resultado = "Judicial"
        elif bens == "Não":
            resultado = "Inventário Negativo"
        else:
            resultado = "Extrajudicial"
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # ATUALIZADO: Enviando o e-mail para o Google Sheets
        # Certifique-se de que a sua folha tem colunas suficientes
        salvar_google([nome, whatsapp, email, resultado, data_hora])
        
        # ATUALIZADO: Enviando o e-mail para o Telegram
        msg = f"🚀 *Novo Lead:*\n👤 *Nome:* {nome}\n📧 *E-mail:* {email}\n📱 *Whats:* {whatsapp}\n⚖️ *Status:* {resultado}"
        enviar_telegram(msg)
        
        st.success(f"### Resultado: {resultado}")
        st.balloons()
        
        # Salvando Leads
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_google([nome, whatsapp, e-mail, cidade, estado, resultado, data_hora])
        enviar_telegram(f"🚀 *Novo Lead:* {nome}\n📱 *Whats:* {whatsapp}\n⚖️ *Status:* {resultado}")

        # MOSTRAR CALENDLY APÓS SUCESSO
        st.markdown("---")
        st.markdown("### Agende sua Reunião Estratégica:")
        # Troque 'SEU-LINK' pelo seu link real do Calendly
        calendly_url = "https://calendly.com/vasconcelosmaia/30min" 
        
        components.html(
            f"""
            <div class="calendly-inline-widget" data-url="{calendly_url}" style="min-width:320px;height:630px;"></div>
            <script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
            """,
            height=650,
        )

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# BOTÕES DE RODAPÉ (SEMPRE VISÍVEIS)
# --- BOTÕES DE RODAPÉ (VERSÃO FINAL SEM ERRO) ---
st.markdown("<h4 style='text-align:center; margin-top:30px; color:white;'>Precisa de ajuda imediata?</h4>", unsafe_allow_html=True)

# Links (Troque o SEU-LINK pelo seu usuário do Calendly)
link_wa = "https://wa.me/5583996498366?text=Olá! Gostaria de falar com um especialista sobre inventário."
link_cal = "https://calendly.com/vasconcelosmaia/30min" 

html_botoes = f"""
<div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-top: 20px;">
    <a href="{link_wa}" target="_blank" style="background-color: #25D366; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; min-width: 210px; text-align: center;">💬 WHATSAPP AGORA</a>
    <a href="{link_cal}" target="_blank" style="background-color: #0A2540; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; min-width: 210px; text-align: center; border: 1px solid #333;">🗓️ MARCAR REUNIÃO AGORA</a>
</div>
"""

st.markdown(html_botoes, unsafe_allow_html=True)

st.markdown(f"""<div class="footer"><hr>© {datetime.now().year} Vasconcelos Maia | Soluções Jurídicas - Atendimento em todo Brasil e Exterior</div>""", unsafe_allow_html=True)
