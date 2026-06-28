import streamlit as st


def _get_valid_token() -> str:
    """Retorna o token válido: primeiro busca nos secrets, depois usa o padrão."""
    try:
        return st.secrets.get("app_token", "admin-token")
    except Exception:
        return "admin-token"


def check_auth():
    """Autentica via token na URL ou via formulário de PIN."""

    # Sessão já autenticada
    if st.session_state.get("authenticated", False):
        return True

    valid_token = _get_valid_token()

    # 1. Tenta autenticar pelo token na URL (?token=...)
    try:
        token = st.query_params.get("token")
        if token and token == valid_token:
            st.session_state["authenticated"] = True
            st.session_state["user_data"] = {"role": "admin", "name": "Admin"}
            return True
    except Exception:
        pass

    # 2. Fallback: formulário de PIN na tela principal
    st.title("🔒 Acesso Restrito")
    st.warning("Este painel é exclusivo para administradores da Dellas.")
    st.markdown("Acesse pelo painel administrativo ou insira o código de acesso:")

    col1, col2 = st.columns([3, 1])
    with col1:
        pin = st.text_input("Código de acesso", type="password",
                            placeholder="Digite o código...", label_visibility="collapsed")
    with col2:
        entrar = st.button("Entrar", use_container_width=True, type="primary")

    if entrar and pin:
        if pin == valid_token:
            st.session_state["authenticated"] = True
            st.session_state["user_data"] = {"role": "admin", "name": "Admin"}
            st.rerun()
        else:
            st.error("Código incorreto.")

    return False

def get_current_user():
    return st.session_state.get("user_data", {})

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
