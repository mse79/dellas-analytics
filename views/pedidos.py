import streamlit as st
import pandas as pd
from components.filters import pedidos_filters, apply_date_filter, apply_status_filter, apply_payment_filter
from services.api import get_pedidos_detalhados
from utils.pdf_generator import gerar_pdf
from utils.formatters import format_currency

st.title("Pedidos 🛒")
st.markdown("Lista completa de pedidos recebidos com filtros detalhados por período, status e pagamento.")

# ── Filtros ────────────────────────────────────────────────────────────────
filters = pedidos_filters()

# ── Carrega dados ──────────────────────────────────────────────────────────
with st.spinner("Carregando pedidos do Firebase..."):
    df_raw = get_pedidos_detalhados()

if df_raw.empty:
    st.warning("Nenhum pedido encontrado na base de dados.")
    st.stop()

# ── Aplica filtros ─────────────────────────────────────────────────────────
df = apply_date_filter(df_raw, filters, date_col="Data")
df = apply_status_filter(df, filters, col="status")
df = apply_payment_filter(df, filters, col="paymentMethod")

# ── KPIs filtrados ─────────────────────────────────────────────────────────
st.subheader("Resumo do Período")

total_pedidos = len(df)
receita = df['Total (R$)'].sum() if not df.empty else 0
ticket = receita / total_pedidos if total_pedidos > 0 else 0
frete_total = df['Frete (R$)'].sum() if not df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Pedidos", total_pedidos)
col2.metric("Faturamento", format_currency(receita))
col3.metric("Ticket Médio", format_currency(ticket))
col4.metric("Total em Frete", format_currency(frete_total))

st.divider()

# ── Gráfico de pedidos por dia ─────────────────────────────────────────────
if not df.empty and 'Data' in df.columns:
    st.subheader("Pedidos por Dia")
    por_dia = df.groupby('Data').agg(
        Pedidos=('id', 'count'),
        Receita=('Total (R$)', 'sum')
    ).reset_index()

    tab1, tab2 = st.tabs(["📦 Quantidade de Pedidos", "💰 Receita por Dia"])
    with tab1:
        st.bar_chart(por_dia.set_index('Data')['Pedidos'])
    with tab2:
        st.bar_chart(por_dia.set_index('Data')['Receita'])

st.divider()

# ── Status breakdown ───────────────────────────────────────────────────────
if not df.empty:
    st.subheader("Distribuição por Status")
    status_df = df.groupby('Status').agg(
        Pedidos=('id', 'count'),
        Receita=('Total (R$)', 'sum')
    ).reset_index()
    status_df['Receita'] = status_df['Receita'].map(format_currency)
    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ── Tabela detalhada ───────────────────────────────────────────────────────
st.subheader(f"Pedidos Detalhados ({total_pedidos} registros)")

# Colunas exibidas
colunas_exibir = ['Data', 'Hora', 'Ref.', 'Cliente', 'Status', 'Pagamento',
                  'Entrega', 'Itens', 'Qtd Itens', 'Subtotal (R$)', 'Frete (R$)', 'Total (R$)']
colunas_disponiveis = [c for c in colunas_exibir if c in df.columns]

if df.empty:
    st.info("Nenhum pedido para o filtro selecionado.")
else:
    df_display = df[colunas_disponiveis].copy()

    # Formata valores monetários
    for col in ['Subtotal (R$)', 'Frete (R$)', 'Total (R$)']:
        if col in df_display.columns:
            df_display[col] = df_display[col].map(format_currency)

    # Colorização por status
    def color_status(val):
        colors = {
            'entregue': 'background-color: #d4edda; color: #155724',
            'confirmado': 'background-color: #cce5ff; color: #004085',
            'pendente': 'background-color: #fff3cd; color: #856404',
            'cancelado': 'background-color: #f8d7da; color: #721c24',
        }
        return colors.get(str(val).lower(), '')

    st.dataframe(
        df_display.style.applymap(color_status, subset=['Status']) if 'Status' in df_display.columns else df_display,
        use_container_width=True,
        hide_index=True
    )

    # ── Botões de Export ───────────────────────────────────────────────
    st.divider()
    col_csv, col_pdf = st.columns(2)

    with col_csv:
        csv = df[colunas_disponiveis].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Exportar CSV",
            data=csv,
            file_name=f"pedidos_{filters['data_inicio']}_{filters['data_fim']}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_pdf:
        kpis_pdf = [
            {"label": "Total de Pedidos", "value": str(total_pedidos)},
            {"label": "Faturamento",      "value": f"R$ {receita:,.2f}"},
            {"label": "Ticket Médio",     "value": f"R$ {ticket:,.2f}"},
            {"label": "Total em Frete",   "value": f"R$ {frete_total:,.2f}"},
        ]
        periodo_label = f"{filters['data_inicio'].strftime('%d/%m/%Y')} a {filters['data_fim'].strftime('%d/%m/%Y')}"
        pdf_bytes = gerar_pdf(
            titulo="Relatório de Pedidos",
            subtitulo=f"Período: {periodo_label}  |  Status: {filters.get('status','Todos')}  |  Pagamento: {filters.get('pagamento','Todas')}",
            df=df[colunas_disponiveis],
            kpis=kpis_pdf,
            secao_tabela="Pedidos Detalhados",
            orientacao="landscape",
        )
        st.download_button(
            label="📄 Exportar PDF",
            data=pdf_bytes,
            file_name=f"pedidos_{filters['data_inicio']}_{filters['data_fim']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
