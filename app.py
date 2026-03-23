import streamlit as st

import requests

import csv



# -----------------------------

# CONFIGURAÇÃO DA PÁGINA

# -----------------------------

st.set_page_config(

    page_title="Inventário Extrajudicial",

    layout="centered",

    page_icon="⚖️"

)



# -----------------------------

# CSS PREMIUM

# -----------------------------

st.markdown("""

<style>

.main-title {

    text-align: center;

    font-size: 34px;

    font-weight: 700;

}



.subtitle {

    text-align: center;

    font-size: 18px;

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

    padding: 12px 24px;

    border-radius: 8px;

    text-decoration: none;

    font-weight: 600;

}



.cta-green {

    display: flex;

    justify-content: center;

    margin: 20px 0;

}



.cta-green a {

    background-color: #2E7D32;

    color: white;

    padding: 12px 24px;

    border-radius: 8px;

    text-decoration: none;

    font-weight: 600;

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

# LOGO CENTRAL

# -----------------------------

col1, col2, col3 = st.columns([1,2,1])

with col2:

    st.image("logo.png", width=200)



# -----------------------------

# HERO SECTION

# -----------------------------

st.markdown('<div class="main-title">Inventário em Cartório de Forma Extrajudicial</div>', unsafe_allow_html=True)

st.markdown('<div class="subtitle">Descubra em poucos minutos se seu caso pode ser resolvido sem processo judicial</div>', unsafe_allow_html=True)



# CTA topo

st.markdown("""
<div style="text-align:center; margin-top:20px;">
    <a href="https://calendly.com/SEU-LINK" target="_blank"
    style="
        background-color:#0A2540;
        color:white;
        padding:14px 28px;
        border-radius:10px;
        text-decoration:none;
        font-weight:bold;
        font-size:16px;
        display:inline-block;
    ">
        AGENDAR AGORA UMA REUNIÃO
    </a>
</div>
""", unsafe_allow_html=True)



# -----------------------------

# FUNÇÕES TELEGRAM

# -----------------------------

TOKEN = "8678540615:AAEY_XhZMuVSOD1FGjz0YRMooIlual9xNPc"

CHAT_ID = "8703766596"



def enviar_telegram(mensagem):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {"chat_id": CHAT_ID, "text": mensagem}

    requests.post(url, data=payload)



# -----------------------------

# FUNÇÃO SALVAR LEAD CSV

# -----------------------------

def salvar_lead(nome, whatsapp, cidade, estado, resultado):

    with open("leads.csv", mode="a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([nome, whatsapp, cidade, estado, resultado])



# -----------------------------

# FUNÇÕES IBGE

# -----------------------------

@st.cache_data

def get_estados():

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    estados = requests.get(url).json()

    estados_ordenados = sorted(estados, key=lambda x: x["nome"])

    return {e["nome"]: e["sigla"] for e in estados_ordenados}



@st.cache_data

def get_cidades(uf):

    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"

    cidades = requests.get(url).json()

    return [c["nome"] for c in cidades]



estados_dict = get_estados()



# -----------------------------

# FORMULÁRIO COMPLETO

# -----------------------------

st.markdown('<div class="section-box">', unsafe_allow_html=True)

st.subheader("Análise gratuita do seu caso")



nome = st.text_input("Nome completo")

whatsapp = st.text_input("WhatsApp")

email = st.text_input("E-mail")



estado_nome = st.selectbox(

    "Estado",

    list(estados_dict.keys()),

    index=None,

    placeholder="Selecione o estado"

)



if estado_nome:

    uf = estados_dict[estado_nome]

    cidades = get_cidades(uf)

    cidade = st.selectbox(

        "Cidade",

        cidades,

        index=None,

        placeholder="Selecione a cidade"

    )

else:

    cidade = None



inventario = st.radio(

    "O inventário já foi iniciado?",

    ["Sim", "Não"],

    index=None

)



data_falecimento = st.date_input(

    "Data do falecimento",

    format="DD/MM/YYYY"

)



herdeiro = st.radio(

    "Existe herdeiro incapaz?",

    ["Sim", "Não"],

    index=None

)



consenso = st.radio(

    "Todos concordam com a divisão?",

    ["Sim", "Não"],

    index=None

)



testamento = st.radio(

    "Existe testamento?",

    ["Sim", "Não", "Não sei"],

    index=None

)



bens = st.radio(

    "Existem bens?",

    ["Sim", "Não"],

    index=None

)



exterior = st.radio(

    "Herdeiro no exterior?",

    ["Sim", "Não"],

    index=None

)



dividas = st.radio(

    "Existem dívidas?",

    ["Sim", "Não", "Não sei"],

    index=None

)



lgpd = st.checkbox(

    "Autorizo o tratamento dos meus dados para análise e contato profissional."

)



# -----------------------------

# BOTÃO ANALISAR

# -----------------------------

if st.button("Analisar caso"):



    if not lgpd:

        st.error("É necessário autorizar o uso dos dados.")

    else:



        # Lógica simplificada de resultado

        if herdeiro == "Sim" or consenso == "Não":

            resultado = "Necessário inventário judicial"

        elif bens == "Não":

            resultado = "Sem bens – avaliar medidas administrativas"

        else:

            resultado = "Possível inventário extrajudicial"



        st.write("---")

        if "extrajudicial" in resultado.lower():

            st.success(resultado)

        elif "judicial" in resultado.lower():

            st.warning(resultado)

        else:

            st.info(resultado)



        # Salvar lead

        salvar_lead(nome, whatsapp, cidade, estado_nome, resultado)



        # Enviar Telegram

        mensagem = f"""

📥 Novo Lead



Nome: {nome}

WhatsApp: {whatsapp}

Cidade: {cidade} - {estado_nome}



Resultado: {resultado}

"""

        enviar_telegram(mensagem)



        # CTA final

        st.markdown("""

        <div class="cta-green">

            <a href="https://calendly.com/SEU-LINK" target="_blank">

                Agendar atendimento com Especialista

            </a>

        </div>

        """, unsafe_allow_html=True)



st.markdown('</div>', unsafe_allow_html=True)



# -----------------------------

# RODAPÉ

# -----------------------------

st.markdown("""

<hr>

<p style='text-align:center; font-size:12px; color:gray;'>

© 2026 Vasconcelos Maia | Soluções Jurídicas. Todos os direitos reservados.  
WhatsApp: +55 (83) 99649-8366

</p>

""", unsafe_allow_html=True)
