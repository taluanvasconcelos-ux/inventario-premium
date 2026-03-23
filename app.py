import streamlit as st
import requests
import csv

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Inventário Extrajudicial",
    layout="centered",
    page_icon="⚖️"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #555;
}

.cta {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

.cta a {
    background-color: #0A2540;
    color: white;
    padding: 14px 28px;
    border-radius: 10px;
    text-decoration: none;
    font-weight: bold;
}

.section-box {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 10px;
    border: 1px solid #eee;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO
# -----------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", width=200)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<h1 class='main-title'>Inventário Extrajudicial com Segurança Jurídica</h1>
<p class='subtitle'>
Análise rápida com especialista. Evite processo judicial desnecessário.
</p>
""", unsafe_allow_html=True)

# CTA PRINCIPAL
st.markdown("""
<div class="cta">
    <a href="https://calendly.com/SEU-LINK" target="_blank">
       AGENDAR REUNIÃO COM UM ESPECIALISTA
    </a>
</div>
""", unsafe_allow_html=True)

st.caption("Ou preencha o formulário para análise")

#whatsapp

st.markdown("""
<div style="text-align:center; margin-top:15px;">
    <a href="wa.me/message/YZO4OMPNQZNSE1?text=Olá,%20quero%20analisar%20meu%20caso%20de%20inventário"
    target="_blank"
    style="
        background-color:#25D366;
        color:white;
        padding:14px 28px;
        border-radius:10px;
        text-decoration:none;
        font-weight:bold;
        display:inline-block;
    ">
        FALAR PELO WHATSAPP AGORA
    </a>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# AUTORIDADE
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-top:20px;">
✔️ Atendimento em todo o Brasil<br>
✔️ Especialistas em inventário extrajudicial<br>
✔️ Atendimento rápido e seguro
</div>
""", unsafe_allow_html=True)

# -----------------------------
# TELEGRAM
# -----------------------------
TOKEN = "8678540615:AAEY_XhZMuVSOD1FGjz0YRMooIlual9xNPc"
CHAT_ID = "8703766596"

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# SALVAR LEAD
# -----------------------------
def salvar_lead(nome, whatsapp, cidade, estado, resultado):
    with open("leads.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nome, whatsapp, cidade, estado, resultado])

# -----------------------------
# IBGE
# -----------------------------
@st.cache_data
def get_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    estados = requests.get(url).json()
    estados = sorted(estados, key=lambda x: x["nome"])
    return {e["nome"]: e["sigla"] for e in estados}

@st.cache_data
def get_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    cidades = requests.get(url).json()
    return [c["nome"] for c in cidades]

estados = get_estados()

# -----------------------------
# FORMULÁRIO
# -----------------------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)

st.subheader("Análise especializada de inventário extrajudicial")

nome = st.text_input("Nome completo")
whatsapp = st.text_input("WhatsApp")
email = st.text_input("E-mail")

estado_nome = st.selectbox("Estado", list(estados.keys()), index=None, placeholder="Selecione o estado")

if estado_nome:
    uf = estados[estado_nome]
    cidades = get_cidades(uf)
    cidade = st.selectbox("Cidade", cidades, index=None, placeholder="Selecione a cidade")
else:
    cidade = None

inventario = st.radio("O inventário já foi iniciado?", ["Sim", "Não"], index=None)

data = st.date_input("Data do falecimento", format="DD/MM/YYYY")

herdeiro = st.radio("Existe herdeiro incapaz?", ["Sim", "Não"], index=None)

consenso = st.radio("Todos concordam com a divisão?", ["Sim", "Não"], index=None)

testamento = st.radio("Existe testamento?", ["Sim", "Não", "Não sei"], index=None)

bens = st.radio("Existem bens?", ["Sim", "Não"], index=None)

exterior = st.radio("Herdeiro no exterior?", ["Sim", "Não"], index=None)

dividas = st.radio("Existem dívidas?", ["Sim", "Não", "Não sei"], index=None)

lgpd = st.checkbox("Autorizo o tratamento dos dados para contato.")

# -----------------------------
# BOTÃO
# -----------------------------
if st.button("Analisar caso"):

    if not lgpd:
        st.error("É necessário aceitar a LGPD.")
    else:

        if herdeiro == "Sim" or consenso == "Não":
            resultado = "Necessário inventário judicial"
            st.warning(resultado)
        elif bens == "Não":
            resultado = "Sem bens — oportunidade administrativa"
            st.info(resultado)
        else:
            resultado = "Forte viabilidade para inventário extrajudicial"
            st.success(resultado)

        # SALVAR
        salvar_lead(nome, whatsapp, cidade, estado_nome, resultado)

        # TELEGRAM
        msg = f"""
🚨 NOVO LEAD

🔥 Status: {resultado}

👤 Nome: {nome}
📱 WhatsApp: {whatsapp}
📍 {cidade} - {estado_nome}
"""
        enviar_telegram(msg)

        # CTA FINAL
        st.markdown("""
        <div class="cta">
            <a href="https://calendly.com/SEU-LINK" target="_blank">
                AGENDAR REUNIÃO COM UM ESPECIALISTA
            </a>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-top:15px;">
    <a href="wa.me/message/YZO4OMPNQZNSE1?text=Olá,%20quero%20analisar%20meu%20caso%20de%20inventário"
    target="_blank"
    style="
        background-color:#25D366;
        color:white;
        padding:14px 28px;
        border-radius:10px;
        text-decoration:none;
        font-weight:bold;
        display:inline-block;
    ">
        FALAR PELO WHATSAPP AGORA
    </a>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# RODAPÉ
# -----------------------------

st.markdown("""
<hr>
<p style='text-align:center; font-size:12px; color:gray;'>
© 2026 Vasconcelos Maia | Soluções Jurídicas. Todos os direitos reservados.  
</p>
""", unsafe_allow_html=True)
