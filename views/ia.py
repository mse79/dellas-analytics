import streamlit as st
from components.filters import global_sidebar_filters
from services.api import get_dashboard_summary, get_revenue_data, get_products_ranking

st.title("Insights Inteligentes 🤖")
st.markdown("Análises automáticas geradas com base nos seus dados reais do Firebase.")

filters = global_sidebar_filters()

summary = get_dashboard_summary(filters)
revenue_df = get_revenue_data(filters)
produtos_df = get_products_ranking(filters)

st.subheader("Resumo Executivo")

receita = summary.get("revenue", 0)
ticket = summary.get("avg_ticket", 0)
operacoes = summary.get("operations", 0)
clientes = summary.get("total_users", 0)
prod_ativos = summary.get("produtos_ativos", 0)

st.success(f"Faturamento total acumulado: **R$ {receita:,.2f}**")
st.info(f"Ticket médio por pedido: **R$ {ticket:,.2f}** com **{operacoes}** operações registradas.")
st.info(f"Base de **{clientes}** clientes cadastrados e **{prod_ativos}** produtos ativos no catálogo.")

st.divider()
st.subheader("Alertas e Anomalias")

if not revenue_df.empty:
    dia_maior = revenue_df.loc[revenue_df['Receita'].idxmax()]
    st.success(f"Melhor dia de vendas: **{dia_maior['Data']}** com R$ {dia_maior['Receita']:,.2f} em receita.")

    if len(revenue_df) > 1:
        ultimo = revenue_df.iloc[-1]['Receita']
        penultimo = revenue_df.iloc[-2]['Receita']
        if ultimo < penultimo * 0.8:
            st.warning("⚠️ Queda de mais de 20% na receita comparado ao dia anterior. Verifique possíveis problemas.")
        elif ultimo > penultimo * 1.2:
            st.success("📈 Alta de mais de 20% na receita no último dia registrado!")

if not produtos_df.empty:
    sem_estoque = (produtos_df['Estoque'] == 0).sum()
    if sem_estoque > 0:
        st.error(f"⚠️ {int(sem_estoque)} produto(s) com estoque zerado. Reposição recomendada.")

if operacoes == 0:
    st.warning("Nenhuma operação de venda registrada ainda.")
