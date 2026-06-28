import streamlit as st
from utils.config import CACHE_TTL

# Wrapper para padronizar o cache de dados vindos da API
def cached_api_call(func):
    """
    Decorator que aplica st.cache_data com TTL padrão definido no config.
    Isso reduz a carga no backend.
    """
    return st.cache_data(ttl=CACHE_TTL, show_spinner=False)(func)

def clear_all_cache():
    """Limpa todo o cache da aplicação Streamlit."""
    st.cache_data.clear()
    st.cache_resource.clear()
