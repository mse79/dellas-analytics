import streamlit as st
from components.filters import financeiro_filters, apply_date_filter
from components.charts import area_chart, bar_chart
from components.tables import smart_table
from services.api import get_revenue_data
from utils.pdf_generator import gerar_pdf
from utils.formatters import format_currency

st.title("Financeiro 💰")
st.markdown("Receitas, custos de comissão e lucro — frete é repasse ao transportador e não entra como despesa.")

filters = financeiro_filters()
df_raw = get_revenue_data(filters)
df = apply_date_filter(df_raw, filters, date_col="Data") if not df_raw.empty else df_raw

if df.empty:
    st.warning("Nenhum dado financeiro encontrado no período.")
else:
    comissao_pct = df['comissao_media'].iloc[0] * 100 if 'comissao_media' in df.columns else 10.0

    # ── KPIs principais ────────────────────────────────────────────────
    st.subheader("Resumo do Período")
    col1, col2, col3, col4 = st.columns(4)

    receita_bruta   = df['Receita'].sum()           # inclui frete cobrado do cliente
    receita_prod    = df['Receita_Produtos'].sum()   # apenas produtos (sem frete)
    frete_total     = df['Frete_Cobrado'].sum()      # frete cobrado (repasse)
    custos_total    = df['Custos'].sum()             # comissões sobre receita de produtos
    lucro_total     = df['Lucro'].sum()              # receita_prod - comissões

    col1.metric("Faturamento Total", format_currency(receita_bruta),
                help="Inclui valor dos produtos + frete cobrado do cliente")
    col2.metric("Receita de Produtos", format_currency(receita_prod),
                help="Apenas valor dos produtos (sem frete)")
    col3.metric("Frete Cobrado (Repasse)", format_currency(frete_total),
                help="Cobrado do cliente e repassado ao transportador — não é lucro da loja")
    col4.metric("Lucro Estimado", format_currency(lucro_total),
                help=f"Receita de produtos menos comissão de {comissao_pct:.0f}%")

    # Linha separada para custos
    col5, col6 = st.columns(2)
    col5.metric(f"Custos (Comissão {comissao_pct:.0f}%)", format_currency(custos_total),
                help="Comissão média dos vendedores cadastrados")
    margem = (lucro_total / receita_prod * 100) if receita_prod > 0 else 0
    col6.metric("Margem Líquida", f"{margem:.1f}%")

    # Nota de transparência
    st.info(
        f"💡 **Metodologia:** Receita de Produtos = Faturamento Total − Frete. "
        f"Custos = {comissao_pct:.0f}% de comissão (média dos vendedores) sobre a Receita de Produtos. "
        f"O frete cobrado do cliente é um repasse ao transportador e **não entra como despesa nem como lucro da loja**."
    )

    st.divider()

    # ── Gráficos ───────────────────────────────────────────────────────
    st.subheader("Receita de Produtos vs Comissões")
    area_chart(df, x="Data", y=["Receita_Produtos", "Custos"],
               title="Receita de Produtos × Custo de Comissão Diário")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        bar_chart(df, x="Data", y="Lucro", title="Lucro Estimado por Dia")
    with col_g2:
        bar_chart(df, x="Data", y="Frete_Cobrado", title="Frete Cobrado por Dia (Repasse)")

    st.divider()

    # ── Tabela detalhada ───────────────────────────────────────────────
    st.subheader("Detalhamento Diário")
    df_display = df[['Data', 'Receita', 'Frete_Cobrado', 'Receita_Produtos', 'Custos', 'Lucro']].copy()
    df_display.columns = ['Data', 'Fat. Total (R$)', 'Frete Repasse (R$)',
                          'Receita Produtos (R$)', 'Comissões (R$)', 'Lucro (R$)']
    for c in df_display.columns[1:]:
        df_display[c] = df_display[c].map(format_currency)
    smart_table(df_display)

    # ── Export ─────────────────────────────────────────────────────────
    st.divider()
    col_csv, col_pdf = st.columns(2)
    periodo_label = f"{filters['data_inicio'].strftime('%d/%m/%Y')} a {filters['data_fim'].strftime('%d/%m/%Y')}"

    with col_csv:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Exportar CSV", data=csv,
            file_name=f"financeiro_{filters['data_inicio']}_{filters['data_fim']}.csv",
            mime="text/csv", use_container_width=True)

    with col_pdf:
        kpis_pdf = [
            {"label": "Fat. Total",          "value": f"R$ {receita_bruta:,.2f}"},
            {"label": "Receita Produtos",     "value": f"R$ {receita_prod:,.2f}"},
            {"label": f"Comissão {comissao_pct:.0f}%", "value": f"R$ {custos_total:,.2f}"},
            {"label": "Frete (Repasse)",      "value": f"R$ {frete_total:,.2f}"},
            {"label": "Lucro Estimado",       "value": f"R$ {lucro_total:,.2f}"},
            {"label": "Margem Líquida",       "value": f"{margem:.1f}%"},
        ]
        pdf_bytes = gerar_pdf(
            titulo="Relatório Financeiro",
            subtitulo=f"Período: {periodo_label}  |  Comissão: {comissao_pct:.0f}%  |  Frete = repasse (não entra como despesa)",
            df=df_display,
            kpis=kpis_pdf,
            secao_tabela="Faturamento Diário",
            orientacao="landscape",
        )
        st.download_button("📄 Exportar PDF", data=pdf_bytes,
            file_name=f"financeiro_{filters['data_inicio']}_{filters['data_fim']}.pdf",
            mime="application/pdf", use_container_width=True)
