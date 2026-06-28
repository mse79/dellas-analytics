import streamlit as st
from components.filters import dashboard_filters
from components.metric_cards import metric_card
from components.charts import line_chart, bar_chart
from services.api import get_dashboard_summary, get_revenue_data
from utils.formatters import format_currency, format_number
from utils.pdf_generator import gerar_pdf

st.title("Painel Executivo 📊")
st.markdown("Visão geral operacional e financeira — dados em tempo real do Firebase.")

filters = dashboard_filters()
summary = get_dashboard_summary(filters)
revenue_df = get_revenue_data(filters)

# ── KPIs ──────────────────────────────────────────────────────────────
st.subheader("Indicadores Principais")
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Receita Total",       format_currency(summary["revenue"]))
with col2:
    metric_card("Ticket Médio",        format_currency(summary["avg_ticket"]))
with col3:
    metric_card("Clientes",            format_number(summary["total_users"]))
with col4:
    metric_card("Total Pedidos",       format_number(summary["operations"]))

col5, col6 = st.columns(2)
with col5:
    metric_card("Produtos Cadastrados", format_number(summary["total_produtos"]))
with col6:
    metric_card("Produtos Ativos",      format_number(summary["produtos_ativos"]))

st.divider()

# ── Gráficos ──────────────────────────────────────────────────────────
if not revenue_df.empty:
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        line_chart(revenue_df, x="Data", y="Receita", title="Evolução de Receita por Dia")
    with col_chart2:
        bar_chart(revenue_df, x="Data", y="Lucro", title="Lucro Estimado por Dia")
else:
    st.info("Nenhum dado de receita encontrado para o período selecionado.")

st.divider()

# ── Export PDF ────────────────────────────────────────────────────────
periodo_label = f"{filters['data_inicio'].strftime('%d/%m/%Y')} a {filters['data_fim'].strftime('%d/%m/%Y')}"

kpis_pdf = [
    {"label": "Receita Total",    "value": format_currency(summary["revenue"])},
    {"label": "Ticket Médio",     "value": format_currency(summary["avg_ticket"])},
    {"label": "Clientes",         "value": format_number(summary["total_users"])},
    {"label": "Total Pedidos",    "value": format_number(summary["operations"])},
    {"label": "Produtos Ativos",  "value": format_number(summary["produtos_ativos"])},
]

pdf_bytes = gerar_pdf(
    titulo="Relatório Executivo",
    subtitulo=f"Período: {periodo_label}",
    df=revenue_df if not revenue_df.empty else None,
    kpis=kpis_pdf,
    secao_tabela="Evolução de Receita Diária",
    orientacao="portrait",
)

st.download_button(
    label="📄 Exportar Relatório Executivo em PDF",
    data=pdf_bytes,
    file_name=f"relatorio_executivo_{filters['data_inicio']}_{filters['data_fim']}.pdf",
    mime="application/pdf",
    use_container_width=True,
)
