"""
App de Controle Financeiro Pessoal — Streamlit + SQLite
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

import database as db
from abas.dashboard import cria_dashboard
from abas.lancamentos import cria_lancamentos
from abas.categorias import cria_categorias
from abas.orcamento import cria_orcamento

st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="wide")
db.init_db()
# ---------------------- ESTILO ----------------------
st.markdown("""
<style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Controle Financeiro Pessoal")

aba = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "➕ Lançamentos", "🏷️ Categorias", "🎯 Orçamento"],
)
if aba == "📊 Dashboard":
# =====================================================
# DASHBOARD
# =====================================================
    df = db.listar_transacoes()
    cria_dashboard(df)
#"""
# =====================================================
# LANÇAMENTOS
# =====================================================
elif aba == "➕ Lançamentos":
    cria_lancamentos()
#"""   
# =====================================================
# CATEGORIAS
# =====================================================
elif aba == "🏷️ Categorias":
    cria_categorias()

# =====================================================
# ORÇAMENTO / METAS
# =====================================================
elif aba == "🎯 Orçamento":
    cria_orcamento()
