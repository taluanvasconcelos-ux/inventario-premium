import streamlit as st
import requests
import csv
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
# ESTILO CSS AVANÇADO (LOOK & FEEL PREMIUM)
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #f8f9fa;
    }

    /* Card Principal */
    .stForm {
        background-color: #ffffff;
        padding: 40px !important;
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }

    /* Títulos */
    .hero-title {
        color: #1a1a1a;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: #666;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 40px;
    }

    /* Botões Customizados */
    div.stButton > button {
        width: 100%;
        background-color: #0A2540 !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #153a5f !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0;
        color: #888;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LÓGICA DE NEGÓCIO & API
# -----------------------------

# Use st.secrets no Streamlit Cloud para não expor tokens!
TOKEN = st.secrets.get("TELEGRAM_TOKEN", "SEU_TOKEN_AQUI")
CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "SEU_CHAT_ID_AQUI")

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Erro ao notificar via Telegram: {e}")

def salvar_lead(dados):
    with open("leads.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=dados.keys())
        if file.tell() == 0: writer.writeheader()
        writer.writerow(dados)

@st.cache_data
def get_estados():
    try:
        response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados")
        estados = sorted(response.json(), key=lambda x: x["nome"])
        return {e["nome"]: e["sigla"] for e in estados}
    except:
        return {"Paraíba": "PB", "São Paulo": "SP"} # Fallback

@st.cache_data
def get_cidades(uf):
    try:
        response = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios")
        return [c["nome"] for c in response.json()]
    except:
        return ["João Pessoa", "Campina Grande"] # Fallback

# -----------------------------
# INTERFACE DO USUÁRIO (UI)
# -----------------------------

# Logo e Header
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    # Substitua pelo caminho da sua logo ou URL
    st.image("https://cdn-icons-png.flaticon.com/512/3504/3504286.png", width=120) 

st.markdown('<h1 class="hero-title">Análise de Inventário</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Descubra a viabilidade do seu processo de forma inteligente e rápida.</p>', unsafe_allow_html=True)

# Formulário Encapsulado
with st.form("analise_form"):
    st.subheader("📝 Dados do Solicitante")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome Completo", placeholder="Ex: João Silva")
        email = st.text_input("E-mail Profissional", placeholder="joao@email.com")
    with c2:
        whatsapp = st.text_input("WhatsApp (com DDD)", placeholder="(83) 99999-9999")
        
        estados_dict = get_estados()
        estado_nome = st.selectbox("Estado", ["Selecione..."] + list(estados_dict.keys()))
    
    cidade = "Não Informada"
    if estado_nome != "Selecione...":
        cidade = st.selectbox("Cidade", get_cidades(estados_dict[estado_nome]))

    st.markdown("---")
    st.subheader("⚖️ Detalhes do Caso")
    
    c3, c4 = st.columns(2)
    with c3:
        inventario_iniciado = st.selectbox("O inventário já foi iniciado?", ["Não", "Sim"])
        herdeiro_incapaz = st.selectbox("Existe herdeiro incapaz (menor ou interdito)?", ["Não", "Sim"])
        tem_bens = st.selectbox("Existem bens a inventariar?", ["Sim", "Não"])
    
    with c4:
        data_obito = st.date_input("Data do Falecimento", format="DD/MM/YYYY")
        consenso = st.selectbox("Todos os herdeiros estão de acordo?", ["Sim", "Não"])
        testamento = st.selectbox("Existe testamento?", ["Não", "Sim", "Não sei"])

    st.markdown("###")
    lgpd = st.checkbox("Estou de acordo com o tratamento dos dados conforme a LGPD.")
    
    submit = st.form_submit_button("GERAR ANÁLISE JURÍDICA")

# -----------------------------
# LÓGICA DE PROCESSAMENTO
# -----------------------------
if submit:
    if not lgpd or not nome or not whatsapp:
        st.warning("⚠️ Por favor, preencha os campos obrigatórios e aceite os termos.")
    else:
        with st.spinner('Analisando legislação vigente...'):
            # Lógica de Classificação
            if herdeiro_incapaz == "Sim" or consenso == "Não":
                tipo_resultado = "JUDICIAL"
                cor_box = "warning"
                detalhe = "Devido à presença de incapazes ou falta de consenso, o caminho obrigatório é a via Judicial."
            elif tem_bens == "Não":
                tipo_resultado = "ADMINISTRATIVO"
                cor_box = "info"
                detalhe = "Sem bens, pode ser necessária apenas uma escritura de inventário negativo."
            else:
                tipo_resultado = "EXTRAJUDICIAL"
                cor_box = "success"
                detalhe = "Seu caso tem grandes chances de ser resolvido em Cartório, sendo muito mais rápido!"

            # Interface de Resultado
            st.markdown(f"### Resultado da Pré-Análise:")
            if tipo_resultado == "EXTRAJUDICIAL":
                st.success(f"**Caminho Recomendado: {tipo_resultado}**\n\n{detalhe}")
                st.balloons()
            elif tipo_resultado == "JUDICIAL":
                st.warning(f"**Caminho Recomendado: {tipo_resultado}**\n\n{detalhe}")
            else:
                st.info(f"**Caminho Recomendado: {tipo_resultado}**\n\n{detalhe}")

            # Persistência de Dados
            dados_lead = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome": nome,
                "WhatsApp": whatsapp,
                "Email": email,
                "Cidade": cidade,
                "UF": estado_nome,
                "Resultado": tipo_resultado
            }
            salvar_lead(dados_lead)

            # Notificação Telegram
            msg_telegram = f"🚀 *Novo Lead de Inventário!*\n\n*Nome:* {nome}\n*Whats:* {whatsapp}\n*Local:* {cidade}/{estado_nome}\n*Resultado:* {tipo_resultado}"
            enviar_telegram(msg_telegram)

            # CTA Final
            st.markdown("---")
            st.markdown("""
                <div style="text-align: center;">
                    <h4>Deseja formalizar este processo agora?</h4>
                    <p>Clique abaixo para agendar uma consulta estratégica.</p>
                    <a href="https://wa.me/5583996498366" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #25D366; color: white; padding: 12px 30px; border-radius: 50px; border: none; font-weight: bold; cursor: pointer;">
                            FALAR COM ESPECIALISTA VIA WHATSAPP
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(f"""
    <div class="footer">
        <hr>
        © {datetime.now().year} Vasconcelos Maia | Advocacia Especializada<br>
        João Pessoa/PB • Atendimento Nacional
    </div>
""", unsafe_allow_html=True)