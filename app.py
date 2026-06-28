import streamlit as st
from services.auth import check_auth, logout
from utils.config import APP_NAME

# Configuração global da página
st.set_page_config(page_title=APP_NAME, layout="wide", initial_sidebar_state="expanded")

# Verificação de Autenticação
if not check_auth():
    st.title("🔒 Acesso Restrito")
    st.warning("Você precisa estar autenticado com um token válido para acessar o módulo de Analytics.")
    st.info("Acesse através do painel administrativo principal.")
    st.stop()

# Definição das Páginas
dashboard = st.Page("views/dashboard.py", title="Dashboard Geral", icon="📊", default=True)
financeiro = st.Page("views/financeiro.py", title="Financeiro", icon="💰")
pedidos = st.Page("views/pedidos.py", title="Pedidos", icon="🛒")
usuarios = st.Page("views/usuarios.py", title="Usuários", icon="👥")
clientes = st.Page("views/clientes.py", title="Clientes", icon="🤝")
produtos = st.Page("views/produtos.py", title="Produtos", icon="📦")
ia = st.Page("views/ia.py", title="Insights IA", icon="🤖")

# Menu de Navegação na Sidebar
pg = st.navigation({
    "Visão Estratégica": [dashboard, financeiro],
    "Operacional": [pedidos, clientes, produtos, usuarios],
    "Sistema": [ia]
})

# Footer da Sidebar
st.sidebar.divider()
if st.sidebar.button("Sair / Limpar Sessão", on_click=logout, use_container_width=True):
    pass

# Renderiza a página selecionada
pg.run()
