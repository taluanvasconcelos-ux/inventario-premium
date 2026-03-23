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
    .main-title { text-align: center; font-size: 36px; font-weight: 700; color: #1a1a1a; margin-bottom: 5px; }
    .subtitle { text-align: center; font-size: 18px; color: #666; margin-bottom: 30px; }
    .cta-container { display: flex; justify-content: center; gap: 15px; margin: 20px 0; flex-wrap: wrap; }
    .btn-calendly { background-color: #0A2540; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }
    .btn-whatsapp { background-color: #25D366; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }
    .section-box { background-color: #ffffff; padding: 30px; border-radius: 15px; border: 1px solid #eee; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO E CABEÇALHO
# -----------------------------
col1, col2, col3 = st.columns([1,1.5,1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown('<h1 class="main-title">Inventário Extrajudicial</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Descubra em 1 minuto se o seu caso é extrajudicial.</p>', unsafe_allow_html=True)

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
st.markdown('<div class="section-box">', unsafe_allow_html=True)
with st.form("form_analise"):
    st.subheader("📍 Pré-Análise do Caso")
    
    nome = st.text_input("Nome completo")
    whatsapp = st.text_input("WhatsApp (com DDD)")
    
    st.write("**Responda abaixo (seleção obrigatória):**")
    
    c1, c2 = st.columns(2)
    with c1:
        # index=None deixa a opção desmarcada por padrão
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
    # Validação de campos vazios
    if None in [herdeiro, consenso, bens, testamento] or not nome or not whatsapp:
        st.error("⚠️ Por favor, preencha todos os campos e selecione todas as opções antes de prosseguir.")
    elif not lgpd:
        st.error("⚠️ Você precisa autorizar o contato (LGPD) para ver o resultado.")
    else:
        # Classificação Jurídica
        if herdeiro == "Sim" or consenso == "Não":
            resultado = "Judicial (Necessário processo em Juízo)"
            st.warning(f"### Resultado: {resultado}")
        elif bens == "Não":
            resultado = "Inventário Negativo (Administrativo)"
            st.info(f"### Resultado: {resultado}")
        else:
            resultado = "Extrajudicial (Forte viabilidade para Cartório)"
            st.success(f"### Resultado: {resultado}")
            st.balloons()
        
        # Salvando Leads
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        salvar_google([nome, whatsapp, resultado, data_hora])
        enviar_telegram(f"🚀 *Novo Lead:* {nome}\n📱 *Whats:* {whatsapp}\n⚖️ *Status:* {resultado}")

        # MOSTRAR CALENDLY APÓS SUCESSO
        st.markdown("---")
        st.markdown("### Agende sua Reunião Estratégica:")
        # Troque 'SEU-LINK' pelo seu link real do Calendly
        calendly_url = "https://calendly.com/SEU-LINK" 
        
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
# -----------------------------
st.markdown("<h4 style='text-align:center; margin-top:30px;'>Precisa de ajuda imediata?</h4>", unsafe_allow_html=True)
st.markdown(f"""
<div class="cta-container">
    <a href="https://wa.me/5583996498366?text=Olá! Vim pelo site e gostaria de falar com um especialista sobre meu caso de inventário." 
       target="_blank" class="btn-whatsapp">💬 WHATSAPP AGORA</a>
    <a href="https://calendly.com/SEU-LINK" target="_blank" class="btn-calendly">🗓️ MARCAR REUNIÃO AGORA</a>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""<div class="footer"><hr>© {datetime.now().year} Vasconcelos Maia | BRASIL</div>""", unsafe_allow_html=True)
