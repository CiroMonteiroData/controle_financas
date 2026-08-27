import streamlit as st
from .estilos import formatar_moeda
def campo_valor_moeda(valor_inicial:float=0.0,label:str="R$", key:str="valor_novo"):
    """
    Campo de valor em reais com máscara estilo caixa eletrônico:
    os dígitos digitados entram da direita para a esquerda,
    sempre respeitando 2 casas decimais. Retorna o valor como float.
    """
    if key not in st.session_state:
        st.session_state[key] = formatar_moeda(valor_inicial)

    def _mascarar():
        digitos = "".join(filter(str.isdigit, st.session_state[key]))
        centavos = int(digitos) if digitos else 0
        st.session_state[key] = formatar_moeda(centavos / 100)

    st.text_input(label, key=key, on_change=_mascarar)

    digitos_atuais = "".join(filter(str.isdigit, st.session_state[key]))
    return (int(digitos_atuais) / 100) if digitos_atuais else 0.0