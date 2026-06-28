import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def line_chart(df: pd.DataFrame, x: str, y: str, title: str):
    """Gera um gráfico de linha interativo."""
    fig = px.line(df, x=x, y=y, title=title, markers=True, template="plotly_white")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color=None):
    """Gera um gráfico de barras interativo."""
    fig = px.bar(df, x=x, y=y, color=color, title=title, template="plotly_white")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

def pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    """Gera um gráfico de pizza interativo."""
    fig = px.pie(df, names=names, values=values, title=title, template="plotly_white", hole=0.4)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

def area_chart(df: pd.DataFrame, x: str, y: list, title: str):
    """Gera gráfico de área."""
    fig = px.area(df, x=x, y=y, title=title, template="plotly_white")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
