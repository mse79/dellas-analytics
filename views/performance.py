import streamlit as st
from components.filters import global_sidebar_filters
from components.charts import line_chart
from services.api import get_system_performance

st.title("Performance & Logs ⚡")
st.markdown("Monitoramento técnico do sistema e saúde da API.")

filters = global_sidebar_filters()
df = get_system_performance(filters)

st.subheader("Latência Média da API")
line_chart(df, x="Hora", y="Latência (ms)", title="Tempo de Resposta em ms")

st.subheader("Erros Detectados")
line_chart(df, x="Hora", y="Erros", title="Taxa de Erros no Período")
