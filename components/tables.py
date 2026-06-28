import streamlit as st
import pandas as pd

def smart_table(df: pd.DataFrame):
    """Exibe um dataframe como tabela interativa."""
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
