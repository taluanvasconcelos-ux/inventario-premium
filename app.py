import streamlit as st
import requests
import csv
import gspread
import json
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
# CSS PREMIUM
# -----------------------------
st.markdown("""
<style>
.main-title { text-align: center; font-size: 38px; font-weight: 700; color: #1a1a1a; }
.subtitle { text-align: center; font-size: 19px; color: #555; margin-bottom: 30px; }
.cta-container { display: flex; justify-content: center; margin: 20px 0; gap: 10px; flex-wrap: wrap; }
.cta-button { 
    background-color: #0A2540; color: white !important; padding: 14px 28px; 
    border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center;
}
.cta-whatsapp { 
    background-color: #25D366; color: white !important; padding: 14px 28px; 
    border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center;
}
.section-box { 
    background-color: #ffffff; padding: 25px; border-radius: 15px; 
    border: 1px solid #eee; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO E HERO
# -----------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown("<h1 class='main-title'>Inventário Extrajudicial com Segurança</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Evite processos demorados. Descubra se seu caso pode ser resolvido em cartório.</p>", unsafe_allow_html=True)

# BOTÕES DE CONTATO RÁPIDO
st.markdown(f"""
<div class="cta-container">
    <a href="https://calendly.com/SEU-LINK" target="_blank" class="cta-button">🗓️ AGENDAR REUNIÃO</a>
    <a href="https://wa.me/5583996498366?text=Olá! Gostaria de uma análise sobre meu caso de Inventário." target="_blank" class="cta-whatsapp">💬 WHATSAPP AGORA</a>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# INTEGRAÇÕES (TELEGRAM E GOOGLE)
# -----------------------------
# MODO SEGURO (Sem vazamento)
TOKEN = st.secrets["TELEGRAM_TOKEN"]
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: 
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        st.error(f"Erro no Telegram: {e}")

def salvar_lead_google(nome, whatsapp, cidade, estado, resultado):
    try:
        # Puxa credenciais dos Secrets do Streamlit Cloud
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha (Certifique-se que ela está compartilhada com o e-mail do bot)
        sheet = client.open("Leads Inventário").sheet1
        sheet.append_row([nome, whatsapp, cidade, estado, resultado, datetime.now().strftime("%d/%m/%Y %H:%M")])
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")

# -----------------------------
# DADOS IBGE
# -----------------------------
@st.cache_data
def get_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    estados_raw = requests.get(url).json()
    estados_raw = sorted(estados_raw, key=lambda x: x["nome"])
    return {e["nome"]: e["sigla"] for e in estados_raw}

@st.cache_data
def get_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    return [c["nome"] for c in requests.get(url).json()]

# -----------------------------
# FORMULÁRIO DE ANÁLISE
# -----------------------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("📝 Formulário de Pré-Análise")

nome = st.text_input("Nome completo")
whatsapp = st.text_input("WhatsApp com DDD")
email = st.text_input("E-mail")

estados_dict = get_estados()
estado_nome = st.selectbox("Estado", list(estados_dict.keys()), index=None, placeholder="Selecione o estado")

cidade = None
if estado_nome:
    cidades = get_cidades(estados_dict[estado_nome])
    cidade = st.selectbox("Cidade", cidades, index=None, placeholder="Selecione a cidade")

# Perguntas Jurídicas
c1, c2 = st.columns(2)
with c1:
    herdeiro = st.radio("Existe herdeiro incapaz (menor)?", ["Não", "Sim"], index=0)
    consenso = st.radio("Todos estão de acordo?", ["Sim", "Não"], index=0)
with c2:
    bens = st.radio("Existem bens a partilhar?", ["Sim", "Não"], index=0)
    testamento = st.radio("Existe testamento?", ["Não", "Sim", "Não sei"], index=0)

lgpd = st.checkbox("Autorizo o tratamento dos dados para contato profissional.")

if st.button("ANALISAR MEU CASO"):
    if not lgpd or not nome or not whatsapp:
        st.error("Por favor, preencha os dados obrigatórios e aceite a LGPD.")
    else:
        # Lógica de Classificação
        if herdeiro == "Sim" or consenso == "Não":
            resultado = "Necessário Inventário Judicial"
            st.warning(f"### {resultado}")
        elif bens == "Não":
            resultado = "Sem bens - Inventário Negativo"
            st.info(f"### {resultado}")
        else:
            resultado = "Forte viabilidade para Extrajudicial (Cartório)"
            st.success(f"### {resultado}")
            st.balloons()

        # EXECUÇÃO DAS INTEGRAÇÕES
        with st.spinner("Salvando seus dados..."):
            # 1. Google Sheets
            salvar_lead_google(nome, whatsapp, cidade, estado_nome, resultado)
            
            # 2. Telegram
            msg_telegram = f"🚀 *Novo Lead:*\n\n*Nome:* {nome}\n*Whats:* {whatsapp}\n*Local:* {cidade}-{estado_nome}\n*Resultado:* {resultado}"
            enviar_telegram(msg_telegram)
            
            st.success("Dados enviados! Nossa equipe entrará em contato.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# RODAPÉ
# -----------------------------
st.markdown(f"""
<hr>
<p style='text-align:center; font-size:12px; color:gray;'>
© {datetime.now().year} Vasconcelos Maia | Soluções Jurídicas<br>
João Pessoa/PB • Atendimento em todo o Brasil
</p>
""", unsafe_allow_html=True)
