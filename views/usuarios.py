import streamlit as st
from components.filters import clientes_filters
from components.tables import smart_table
from services.api import get_users_data

st.title("Usuários 👥")
st.markdown("Base de usuários/clientes cadastrados no sistema.")

filters = clientes_filters()
df = get_users_data(filters)

if df.empty or 'nome' not in df.columns:
    st.warning("Nenhum usuário encontrado na base de dados.")
else:
    # ── Métricas ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Usuários", len(df))
    with col2:
        com_email = df['email'].astype(str).str.strip().ne('').sum() if 'email' in df.columns else 0
        st.metric("Com Email", int(com_email))
    with col3:
        com_tel = df['telefone'].astype(str).str.strip().ne('').sum() if 'telefone' in df.columns else 0
        st.metric("Com Telefone", int(com_tel))

    st.divider()

    # ── Tabela completa ────────────────────────────────────────────────
    st.subheader("Lista de Usuários")
    colunas = [c for c in ['nome', 'email', 'telefone', 'criadoEm'] if c in df.columns]
    smart_table(df[colunas] if colunas else df)
