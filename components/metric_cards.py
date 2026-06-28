import streamlit as st

def metric_card(title: str, value: str, subtitle: str = "", delta: str = None, delta_color: str = "normal"):
    """
    Renderiza um cartão de KPI com visual moderno usando st.metric ou HTML/CSS.
    """
    # Using native st.metric with delta for modern Streamlit styling
    st.metric(label=title, value=value, delta=delta, delta_color=delta_color)
