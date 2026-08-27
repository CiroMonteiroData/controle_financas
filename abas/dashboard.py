import pandas as pd
import streamlit as st
import plotly.express as px
from utils.estilos import MESES_PT, formatar_moeda
def cria_dashboard(df:pd.DataFrame):
    if df.empty:
        st.info("Nenhuma transação cadastrada ainda. Vá em **Lançamentos** para adicionar a primeira.")
    else:
        df["ano_mes"] = df["data"].dt.to_period("M").astype(str)

        col_f1, col_f2 = st.columns(2)
        anos = sorted(df["data"].dt.year.unique(), reverse=True)
        ano_sel = col_f1.selectbox("Ano", anos)
        meses_disponiveis = sorted(df[df["data"].dt.year == ano_sel]["data"].dt.month.unique())
        opcoes_mes = ["Todos"] + [MESES_PT[m] for m in meses_disponiveis]
        mes_sel = col_f2.selectbox("Mês", opcoes_mes)

        df_filtrado = df[df["data"].dt.year == ano_sel]
        if mes_sel != "Todos":
            mes_num = [k for k, v in MESES_PT.items() if v == mes_sel][0]
            df_filtrado = df_filtrado[df_filtrado["data"].dt.month == mes_num]

        receitas = df_filtrado[df_filtrado["tipo"] == "Receita"]["valor"].sum()
        despesas = df_filtrado[df_filtrado["tipo"] == "Despesa"]["valor"].sum()
        saldo = receitas - despesas

        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", formatar_moeda(receitas))
        c2.metric("Despesas", formatar_moeda(despesas))
        c3.metric("Saldo", formatar_moeda(saldo), delta=formatar_moeda(saldo))

        st.divider()

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Despesas por categoria")
            desp_cat = df_filtrado[df_filtrado["tipo"] == "Despesa"].groupby("categoria")["valor"].sum().reset_index()
            if not desp_cat.empty:
                fig = px.pie(desp_cat, names="categoria", values="valor", hole=0.4)
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Sem despesas no período selecionado.")

        with col_g2:
            st.subheader("Receitas por categoria")
            rec_cat = df_filtrado[df_filtrado["tipo"] == "Receita"].groupby("categoria")["valor"].sum().reset_index()
            if not rec_cat.empty:
                fig = px.pie(rec_cat, names="categoria", values="valor", hole=0.4)
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Sem receitas no período selecionado.")

        st.divider()
        st.subheader("Evolução mensal (Receitas x Despesas)")
        evolucao = df.groupby(["ano_mes", "tipo"])["valor"].sum().reset_index()
        if not evolucao.empty:
            fig2 = px.bar(
                evolucao, x="ano_mes", y="valor", color="tipo", barmode="group",
                labels={"ano_mes": "Mês", "valor": "Valor (R$)", "tipo": "Tipo"},
                color_discrete_map={"Receita": "#2ecc71", "Despesa": "#e74c3c"},
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("Últimas transações")
        st.dataframe(
            df_filtrado[["data", "tipo", "categoria", "descricao", "valor"]]
            .sort_values("data", ascending=False)
            .assign(data=lambda d: d["data"].dt.strftime("%d/%m/%Y"))
            .head(15),
            use_container_width=True, hide_index=True,
        )
