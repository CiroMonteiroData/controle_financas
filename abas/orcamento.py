import streamlit as st
import pandas as pd
import database as db
from datetime import date
from utils.estilos import MESES_PT, formatar_moeda
from utils.misc_func import campo_valor_moeda
def cria_orcamento():
    st.subheader("Definir metas mensais por categoria")
    
    hoje = date.today()
    c1, c2 = st.columns(2)
    ano_orc = c1.selectbox("Ano", range(hoje.year - 1, hoje.year + 2), index=1)
    mes_orc_nome = c2.selectbox("Mês", list(MESES_PT.values()), index=hoje.month - 1)
    mes_orc_num = [k for k, v in MESES_PT.items() if v == mes_orc_nome][0]
    mes_str = f"{ano_orc}-{mes_orc_num:02d}"

    categorias_despesa = db.listar_categorias("Despesa")["nome"].tolist()

    with st.form("form_orcamento", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cat_orc = c1.selectbox("Categoria", categorias_despesa)
        limite = c2.number_input("Limite mensal (R$)", min_value=0.0, step=50.0, format="%.2f")
        if st.form_submit_button("Salvar meta"):
            db.definir_orcamento(cat_orc, mes_str, limite)
            st.success(f"Meta de {formatar_moeda(limite)} definida para {cat_orc} em {mes_orc_nome}/{ano_orc}.")
            st.rerun()

    st.divider()
    st.subheader(f"Progresso — {mes_orc_nome}/{ano_orc}")

    orcamentos = db.listar_orcamentos(mes_str)
    if orcamentos.empty:
        st.caption("Nenhuma meta definida para esse mês ainda.")
    else:
        transacoes = db.listar_transacoes()
        if not transacoes.empty:
            transacoes["ano_mes"] = transacoes["data"].dt.to_period("M").astype(str)
            gastos_mes = transacoes[
                (transacoes["ano_mes"] == mes_str) & (transacoes["tipo"] == "Despesa")
            ].groupby("categoria")["valor"].sum()
        else:
            gastos_mes = pd.Series(dtype=float)

        for _, row in orcamentos.iterrows():
            gasto = gastos_mes.get(row["categoria"], 0.0)
            limite = row["limite"]
            pct = min(gasto / limite, 1.0) if limite > 0 else 0

            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"**{row['categoria']}** — {formatar_moeda(gasto)} de {formatar_moeda(limite)}")
                cor_barra = "normal" if pct < 0.8 else ("normal" if pct < 1.0 else "normal")
                st.progress(pct)
                if gasto > limite:
                    st.error(f"Estourou o orçamento em {formatar_moeda(gasto - limite)}!")
                elif pct >= 0.8:
                    st.warning("Perto do limite!")
            with col_b:
                st.write("")
                if st.button("🗑️ Remover", key=f"orc_{row['id']}"):
                    db.remover_orcamento(row["id"])
                    st.rerun()
    