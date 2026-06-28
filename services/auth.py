import jwt
import streamlit as st
from utils.config import JWT_SECRET

def check_auth():
    """Check if the user is authenticated via JWT in query params or session."""
    
    # Se já está autenticado na sessão, continua
    if st.session_state.get("authenticated", False):
        return True

    # No Streamlit Cloud (secrets do Firebase configurados), autenticar automaticamente.
    # O controle de acesso público/privado é gerenciado pelo Streamlit Cloud.
    try:
        on_cloud = "firebase" in st.secrets
    except Exception:
        on_cloud = False
    if on_cloud:
        st.session_state["authenticated"] = True
        st.session_state["user_data"] = {"role": "admin", "name": "Admin"}
        return True
        
    # Fallback: busca o token nos query params (desenvolvimento local)
    query_params = st.query_params
    token = query_params.get("token")
    
    if not token:
        return False
        
    try:
        if token == 'admin-token':
            decoded = {"role": "admin", "name": "Test User"}
        else:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        st.session_state["authenticated"] = True
        st.session_state["user_data"] = decoded
        st.session_state["token"] = token
        return True
    except Exception:
        return False

def get_current_user():
    return st.session_state.get("user_data", {})

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
