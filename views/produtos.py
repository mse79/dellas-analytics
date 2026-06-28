import streamlit as st
import pandas as pd
from components.filters import produtos_filters
from services.api import get_produtos_com_vendas
from utils.pdf_generator import gerar_pdf
from utils.formatters import format_currency

st.title("Produtos 📦")
st.markdown("Análise de desempenho, estoque e ranking de vendas — dados reais do Firebase.")

filters = produtos_filters()

with st.spinner("Carregando produtos e cruzando com vendas..."):
    df = get_produtos_com_vendas()

if df.empty:
    st.warning("Nenhum produto encontrado na base de dados.")
    st.stop()

# ── Métricas Gerais ────────────────────────────────────────────────────────
st.subheader("Visão Geral")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Produtos", len(df))
col2.metric("Produtos Ativos",   int(df['ativo'].sum()))
col3.metric("Estoque Total",     int(df['estoque'].sum()))
col4.metric("Unidades Vendidas", int(df['Qtd Vendida'].sum()))

st.divider()

# ── 1. MAIS VENDIDOS ───────────────────────────────────────────────────────
st.subheader("🏆 Produtos Mais Vendidos")
mais_vendidos = (
    df[df['Qtd Vendida'] > 0]
    .sort_values('Qtd Vendida', ascending=False)
    .head(10)
    .reset_index(drop=True)
)

if mais_vendidos.empty:
    st.info("Nenhum produto com venda registrada ainda.")
else:
    # Gráfico horizontal de barras
    st.bar_chart(mais_vendidos.set_index('nome')['Qtd Vendida'])

    # Cards Top 5
    st.markdown("**Top 5:**")
    top5_cols = st.columns(5)
    for i, (_, row) in enumerate(mais_vendidos.head(5).iterrows()):
        with top5_cols[i]:
            st.markdown(f"**{row['nome']}**")
            st.caption(f"SKU: {row.get('sku', '—')}")
            st.caption(f"Vendas: {row['Qtd Vendida']} un.")
            st.caption(format_currency(row['preco']))

    # Tabela completa
    with st.expander("Ver tabela completa — Mais Vendidos"):
        cols_show = ['sku', 'nome', 'categoria', 'preco', 'estoque', 'Qtd Vendida', 'Receita Vendas (R$)']
        cols_show = [c for c in cols_show if c in mais_vendidos.columns]
        st.dataframe(mais_vendidos[cols_show], use_container_width=True, hide_index=True)

st.divider()

# ── 2. MENOS VENDIDOS ──────────────────────────────────────────────────────
st.subheader("📉 Produtos Menos Vendidos")
ativos = df[df['ativo'] == True].copy()
menos_vendidos = ativos.sort_values('Qtd Vendida', ascending=True).head(10).reset_index(drop=True)

if menos_vendidos.empty:
    st.info("Sem dados suficientes.")
else:
    # Cards Top 5 menos vendidos
    menos_cols = st.columns(min(5, len(menos_vendidos)))
    for i, (_, row) in enumerate(menos_vendidos.head(5).iterrows()):
        with menos_cols[i]:
            st.markdown(f"**{row['nome']}**")
            st.caption(f"SKU: {row.get('sku', '—')}")
            st.caption(f"Vendas: {row['Qtd Vendida']} un.")
            st.caption(f"Estoque: {row['estoque']}")

    with st.expander("Ver tabela completa — Menos Vendidos"):
        cols_show = ['sku', 'nome', 'categoria', 'preco', 'estoque', 'Qtd Vendida']
        cols_show = [c for c in cols_show if c in menos_vendidos.columns]
        st.dataframe(menos_vendidos[cols_show], use_container_width=True, hide_index=True)

st.divider()

# ── 3. ESTOQUE BAIXO ───────────────────────────────────────────────────────
LIMITE_ESTOQUE_BAIXO = 5
st.subheader(f"⚠️ Estoque Baixo (≤ {LIMITE_ESTOQUE_BAIXO} unidades)")

estoque_baixo = (
    df[(df['ativo'] == True) & (df['estoque'] <= LIMITE_ESTOQUE_BAIXO)]
    .sort_values('estoque', ascending=True)
    .reset_index(drop=True)
)

if estoque_baixo.empty:
    st.success("✅ Nenhum produto com estoque crítico no momento.")
else:
    st.error(f"**{len(estoque_baixo)} produto(s)** com estoque crítico! Reposição urgente recomendada.")

    # Cards estoque crítico
    eb_cols = st.columns(min(5, len(estoque_baixo)))
    for i, (_, row) in enumerate(estoque_baixo.head(5).iterrows()):
        with eb_cols[i]:
            st.markdown(f"**{row['nome']}**")
            st.caption(f"SKU: {row.get('sku', '—')}")
            estoque_val = int(row['estoque'])
            if estoque_val == 0:
                st.error(f"🔴 Estoque: **{estoque_val}**")
            else:
                st.warning(f"🟡 Estoque: **{estoque_val}**")
            st.caption(format_currency(row['preco']))

    with st.expander("Ver tabela completa — Estoque Crítico"):
        cols_show = ['sku', 'nome', 'categoria', 'preco', 'estoque', 'Qtd Vendida']
        cols_show = [c for c in cols_show if c in estoque_baixo.columns]

        def highlight_estoque(val):
            if val == 0:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return 'background-color: #fff3cd; color: #856404'

        st.dataframe(
            estoque_baixo[cols_show].style.applymap(highlight_estoque, subset=['estoque']),
            use_container_width=True,
            hide_index=True
        )

st.divider()

# ── 4. CATÁLOGO COMPLETO ──────────────────────────────────────────────────
st.subheader("📋 Catálogo Completo")

# Filtro por categoria
cats = ["Todas"] + sorted(df['categoria'].dropna().unique().tolist())
cat_sel = st.selectbox("Filtrar por Categoria", cats)
df_cat = df if cat_sel == "Todas" else df[df['categoria'] == cat_sel]

cols_cat = ['sku', 'nome', 'categoria', 'preco', 'precoPromocional', 'estoque', 'ativo', 'Qtd Vendida', 'Receita Vendas (R$)']
cols_cat = [c for c in cols_cat if c in df_cat.columns]
st.dataframe(
    df_cat[cols_cat].sort_values('Qtd Vendida', ascending=False),
    use_container_width=True,
    hide_index=True
)

# ── Export PDF ─────────────────────────────────────────────────────────────
st.divider()
col_csv, col_pdf = st.columns(2)

with col_csv:
    csv = df[cols_cat].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Exportar CSV",
        data=csv,
        file_name="produtos_ranking.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_pdf:
    kpis_pdf = [
        {"label": "Total Produtos",    "value": str(len(df))},
        {"label": "Ativos",            "value": str(int(df['ativo'].sum()))},
        {"label": "Estoque Crítico",   "value": str(len(estoque_baixo))},
        {"label": "Unidades Vendidas", "value": str(int(df['Qtd Vendida'].sum()))},
    ]
    df_pdf = df[cols_cat].sort_values('Qtd Vendida', ascending=False)
    pdf_bytes = gerar_pdf(
        titulo="Relatório de Produtos",
        subtitulo="Ranking de vendas, estoque crítico e catálogo completo",
        df=df_pdf,
        kpis=kpis_pdf,
        secao_tabela="Catálogo com Ranking de Vendas",
        orientacao="landscape",
    )
    st.download_button(
        label="📄 Exportar PDF",
        data=pdf_bytes,
        file_name="produtos_ranking.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
