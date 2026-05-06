import streamlit as st
import streamlit.components.v1 as components


NEW_SITE_URL = "https://inventarioextra.vercel.app/formulario"

st.set_page_config(
    page_title="Inventário Extrajudicial | Taluã Maia",
    layout="centered",
    page_icon="⚖️",
)

components.html(
    f"""
    <script>
      window.top.location.href = "{NEW_SITE_URL}";
    </script>
    <meta http-equiv="refresh" content="0; url={NEW_SITE_URL}" />
    """,
    height=0,
)

st.markdown(
    """
    <style>
      .block-container {
        max-width: 720px;
        padding-top: 5rem;
      }

      .redirect-card {
        border: 1px solid #d8c7a5;
        border-radius: 12px;
        padding: 32px;
        background: #fffaf1;
        text-align: center;
        color: #1c1917;
      }

      .redirect-card h1 {
        font-size: 30px;
        line-height: 1.2;
        margin-bottom: 12px;
      }

      .redirect-card p {
        color: #57534e;
        font-size: 16px;
        line-height: 1.7;
      }

      .redirect-card a {
        display: inline-block;
        margin-top: 20px;
        padding: 12px 18px;
        border-radius: 8px;
        background: #14110c;
        color: #f3dfad !important;
        text-decoration: none;
        font-weight: 700;
      }
    </style>

    <div class="redirect-card">
      <h1>Redirecionando para o novo diagnóstico sucessório</h1>
      <p>
        A triagem de inventário extrajudicial agora está em uma nova página,
        com análise mais completa, LGPD/GDPR, WhatsApp e agendamento de reunião.
      </p>
      <a href="https://inventarioextra.vercel.app/formulario" target="_top">
        Acessar novo site
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)
