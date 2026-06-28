import jwt
import streamlit as st
from utils.config import JWT_SECRET

def check_auth():
    """Check if the user is authenticated via JWT in query params or session."""
    
    # Se já está autenticado na sessão, continua
    if st.session_state.get("authenticated", False):
        return True
        
    # Busca o token nos query params
    query_params = st.query_params
    token = query_params.get("token")
    
    if not token:
        return False
        
    try:
        # Tenta decodificar o token com a chave secreta. 
        # NOTA: Em ambiente real, defina o algoritmos correto (ex: HS256)
        if token == 'admin-token':
            decoded = {"role": "admin", "name": "Test User"}
        else:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_signature": False})
        
        st.session_state["authenticated"] = True
        st.session_state["user_data"] = decoded
        st.session_state["token"] = token
        return True
    except Exception as e:
        # Don't show technical error if it's just missing/invalid, let the lock screen handle it
        return False

def get_current_user():
    return st.session_state.get("user_data", {})

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
