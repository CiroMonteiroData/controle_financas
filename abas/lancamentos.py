import streamlit as st
import database as db
from datetime import date
from utils.estilos import MESES_PT, formatar_moeda
from utils.misc_func import campo_valor_moeda

def cria_lancamentos():
    st.subheader("Adicionar nova transação")
    tipo = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True)
    categorias_df = db.listar_categorias(tipo)
    with st.form("form_transacao", clear_on_submit=True):
        c1, c2 = st.columns(2)
        data_transacao = c1.date_input("Data", value=date.today(),format="DD/MM/YYYY")
        if categorias_df.empty:
            c2.warning("Nenhuma categoria cadastrada para esse tipo. Crie uma na aba Categorias.")
            categoria = None
        else:
            categoria = c2.selectbox("Categoria", categorias_df["nome"].tolist())

        descricao = st.text_input("Descrição (opcional)")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
        #valor = campo_valor_moeda()

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

    if "editando_id" not in st.session_state:
        st.session_state.editando_id = None

    df = db.listar_transacoes()
    if df.empty:
        st.caption("Nenhuma transação cadastrada.")
    else:
        for _, row in df.iterrows():
            cols = st.columns([1.2, 1, 1.5, 2.5, 1.2, 0.5, 0.5])
            cols[0].write(row["data"].strftime("%d/%m/%Y"))
            cols[1].write(row["tipo"])
            cols[2].write(row["categoria"])
            cols[3].write(row["descricao"] or "—")
            cor = "green" if row["tipo"] == "Receita" else "red"
            cols[4].markdown(f":{cor}[{formatar_moeda(row['valor'])}]")
            if cols[5].button("✏️", key=f"edit_{row['id']}"):
                st.session_state.editando_id = row["id"]
                st.rerun()
            if cols[6].button("🗑️", key=f"del_{row['id']}"):
                db.remover_transacao(row["id"])
                st.rerun()

            if st.session_state.editando_id == row["id"]:
                with st.container(border=True):
                    st.markdown(f"**Editando transação #{row['id']}**")
                    with st.form(f"form_editar_{row['id']}"):
                        e1, e2 = st.columns(2)
                        nova_data = e1.date_input("Data", value=row["data"].date(), key=f"edata_{row['id']}",format="DD/MM/YYYY")
                        novo_tipo = e2.selectbox(
                            "Tipo", ["Receita", "Despesa"],
                            index=0 if row["tipo"] == "Receita" else 1,
                            key=f"etipo_{row['id']}",
                        )
                        cats_disponiveis = db.listar_categorias(novo_tipo)["nome"].tolist()
                        idx_cat = cats_disponiveis.index(row["categoria"]) if row["categoria"] in cats_disponiveis else 0
                        nova_categoria = st.selectbox(
                            "Categoria", cats_disponiveis, index=idx_cat, key=f"ecat_{row['id']}"
                        )
                        nova_descricao = st.text_input(
                            "Descrição", value=row["descricao"] or "", key=f"edesc_{row['id']}"
                        )
                        novo_valor = st.number_input(
                            "Valor (R$)", min_value=0.0, step=10.0, format="%.2f",
                            value=float(row["valor"]), key=f"eval_{row['id']}",
                        )

                        salvar_col, cancelar_col = st.columns(2)
                        if salvar_col.form_submit_button("💾 Salvar alterações", use_container_width=True):
                            if novo_valor <= 0:
                                st.error("Informe um valor maior que zero.")
                            else:
                                db.atualizar_transacao(
                                    row["id"], nova_data.isoformat(), novo_tipo,
                                    nova_categoria, nova_descricao, novo_valor,
                                )
                                st.session_state.editando_id = None
                                st.success("Transação atualizada!")
                                st.rerun()
                        if cancelar_col.form_submit_button("Cancelar", use_container_width=True):
                            st.session_state.editando_id = None
                            st.rerun()