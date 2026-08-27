"""
App de Controle Financeiro Pessoal — Streamlit + SQLite
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

import database as db

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

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def formatar_moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =====================================================
# DASHBOARD
# =====================================================
if aba == "📊 Dashboard":
    df = db.listar_transacoes()

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

# =====================================================
# LANÇAMENTOS
# =====================================================
elif aba == "➕ Lançamentos":
    st.subheader("Adicionar nova transação")

    tipo = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True)
    categorias_df = db.listar_categorias(tipo)

    with st.form("form_transacao", clear_on_submit=True):
        c1, c2 = st.columns(2)
        data_transacao = c1.date_input("Data", value=date.today())
        if categorias_df.empty:
            c2.warning("Nenhuma categoria cadastrada para esse tipo. Crie uma na aba Categorias.")
            categoria = None
        else:
            categoria = c2.selectbox("Categoria", categorias_df["nome"].tolist())

        descricao = st.text_input("Descrição (opcional)")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")

        enviado = st.form_submit_button("Salvar transação", use_container_width=True)
        if enviado:
            if not categoria:
                st.error("Cadastre uma categoria antes de lançar a transação.")
            elif valor <= 0:
                st.error("Informe um valor maior que zero.")
            else:
                db.adicionar_transacao(data_transacao.isoformat(), tipo, categoria, descricao, valor)
                st.success("Transação adicionada com sucesso!")
                st.rerun()

    st.divider()
    st.subheader("Transações cadastradas")

    df = db.listar_transacoes()
    if df.empty:
        st.caption("Nenhuma transação cadastrada.")
    else:
        for _, row in df.iterrows():
            cols = st.columns([1.2, 1, 1.5, 2.5, 1.2, 0.6])
            cols[0].write(row["data"].strftime("%d/%m/%Y"))
            cols[1].write(row["tipo"])
            cols[2].write(row["categoria"])
            cols[3].write(row["descricao"] or "—")
            cor = "green" if row["tipo"] == "Receita" else "red"
            cols[4].markdown(f":{cor}[{formatar_moeda(row['valor'])}]")
            if cols[5].button("🗑️", key=f"del_{row['id']}"):
                db.remover_transacao(row["id"])
                st.rerun()

# =====================================================
# CATEGORIAS
# =====================================================
elif aba == "🏷️ Categorias":
    st.subheader("Gerenciar categorias")

    with st.form("form_categoria", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        nome_cat = c1.text_input("Nome da categoria")
        tipo_cat = c2.selectbox("Tipo", ["Receita", "Despesa"])
        if st.form_submit_button("Adicionar categoria"):
            if nome_cat.strip():
                ok, msg = db.adicionar_categoria(nome_cat.strip(), tipo_cat)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()
            else:
                st.error("Digite um nome para a categoria.")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Receitas**")
        df_r = db.listar_categorias("Receita")
        for _, row in df_r.iterrows():
            c1_, c2_ = st.columns([4, 1])
            c1_.write(row["nome"])
            if c2_.button("🗑️", key=f"cat_r_{row['id']}"):
                db.remover_categoria(row["id"])
                st.rerun()

    with col2:
        st.markdown("**Despesas**")
        df_d = db.listar_categorias("Despesa")
        for _, row in df_d.iterrows():
            c1_, c2_ = st.columns([4, 1])
            c1_.write(row["nome"])
            if c2_.button("🗑️", key=f"cat_d_{row['id']}"):
                db.remover_categoria(row["id"])
                st.rerun()

# =====================================================
# ORÇAMENTO / METAS
# =====================================================
elif aba == "🎯 Orçamento":
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
