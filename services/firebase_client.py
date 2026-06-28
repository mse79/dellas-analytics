import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st
from utils.config import FIREBASE_CREDENTIALS_PATH


@st.cache_resource
def get_firestore_client():
    """Inicializa e retorna o cliente do Firestore usando arquivo local ou segredos do Streamlit."""
    if not firebase_admin._apps:
        # 1. Se estiver rodando na Nuvem do Streamlit (usando Secrets)
        if "firebase" in st.secrets:
            try:
                # Converte o dicionário de segredos em credencial
                cred_info = dict(st.secrets["firebase"])
                # Corrige quebras de linha na chave privada
                if "private_key" in cred_info:
                    cred_info["private_key"] = cred_info["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(cred_info)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error("Erro ao inicializar Firebase na nuvem: " + str(e))
                st.stop()
        # 2. Se estiver rodando localmente (usando o arquivo .json)
        else:
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                st.error("Credenciais do Firebase nao encontradas localmente em: " + FIREBASE_CREDENTIALS_PATH)
                st.info("Coloque o arquivo firebase-adminsdk.json na pasta analytics/credentials/")
                st.stop()

            try:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error("Erro ao inicializar Firebase local: " + str(e))
                st.stop()

    return firestore.client()
