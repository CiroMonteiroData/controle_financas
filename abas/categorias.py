import streamlit as st
import database as db

def cria_categorias():
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