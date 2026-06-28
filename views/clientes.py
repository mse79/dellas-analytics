import streamlit as st
from components.filters import clientes_filters, apply_date_filter
from components.tables import smart_table
from services.api import get_users_data

st.title("Clientes 🤝")
st.markdown("Base de clientes cadastrados — dados reais do Firebase.")

filters = clientes_filters()
df = get_users_data(filters)

if df.empty or (len(df.columns) == 2 and "Status" in df.columns):
    st.warning("Nenhum cliente encontrado ou erro ao carregar dados.")
else:
    # ── Métricas ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Clientes", len(df))
    with col2:
        com_telefone = df['telefone'].astype(str).str.strip().ne('').sum() if 'telefone' in df.columns else 0
        st.metric("Com Telefone", int(com_telefone))

    st.divider()

    # ── Tabela ─────────────────────────────────────────────────────────
    st.subheader("Lista de Clientes")
    colunas = [c for c in ['nome', 'email', 'telefone', 'criadoEm'] if c in df.columns]
    smart_table(df[colunas] if colunas else df)
