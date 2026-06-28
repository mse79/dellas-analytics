import streamlit as st


def _get_senha() -> str:
    """Retorna a senha configurada nos secrets ou o padrão."""
    try:
        return st.secrets.get("app_token", "admin-token")
    except Exception:
        return "admin-token"


def check_auth():
    """Autentica sempre via formulário de senha."""

    # Sessão já autenticada
    if st.session_state.get("authenticated", False):
        return True

    # Tela de login centralizada
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🛒 Dellas")
        st.subheader("🔒 Painel Analytics")
        st.caption("Área restrita — somente administradores.")

        senha = st.text_input("Senha", type="password",
                              placeholder="Digite sua senha de 8 dígitos",
                              max_chars=8)
        entrar = st.button("Entrar", use_container_width=True, type="primary")

        if entrar:
            if senha == _get_senha():
                st.session_state["authenticated"] = True
                st.session_state["user_data"] = {"role": "admin", "name": "Admin"}
                st.rerun()
            else:
                st.error("Senha incorreta.")

    return False

def get_current_user():
    return st.session_state.get("user_data", {})

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
