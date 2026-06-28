import streamlit as st
from datetime import date, timedelta
from utils.constants import PERIODOS, STATUS_PEDIDOS


def _resolve_date_range(periodo: str):
    """Converte o período selecionado em (data_inicio, data_fim)."""
    hoje = date.today()
    if periodo == "Hoje":
        return hoje, hoje
    elif periodo == "Últimos 7 dias":
        return hoje - timedelta(days=7), hoje
    elif periodo == "Últimos 30 dias":
        return hoje - timedelta(days=30), hoje
    elif periodo == "Mês Atual":
        return hoje.replace(day=1), hoje
    elif periodo == "Mês Passado":
        primeiro_deste = hoje.replace(day=1)
        ultimo_mes = primeiro_deste - timedelta(days=1)
        return ultimo_mes.replace(day=1), ultimo_mes
    elif periodo == "Últimos 3 Meses":
        return hoje - timedelta(days=90), hoje
    elif periodo == "Ano Atual":
        return hoje.replace(month=1, day=1), hoje
    else:  # "Todo o Período"
        return date(2020, 1, 1), hoje


def _render_date_filter(page_key: str):
    """Auxiliar para renderizar o filtro de data padrão com chaves isoladas por página."""
    st.sidebar.subheader("📅 Período")
    
    # Estado inicial na sessão para evitar perda de valor ao navegar
    periodo_key = f"{page_key}_periodo"
    if periodo_key not in st.session_state:
        st.session_state[periodo_key] = "Últimos 30 dias"
        
    idx = PERIODOS.index(st.session_state[periodo_key]) if st.session_state[periodo_key] in PERIODOS else 2
    periodo = st.sidebar.selectbox("Selecionar Período", PERIODOS, index=idx, key=periodo_key)
    
    filters = {}
    if periodo == "Personalizado":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            data_ini = st.date_input("De", value=date.today() - timedelta(days=30), key=f"{page_key}_date_ini")
        with col2:
            data_fim = st.date_input("Até", value=date.today(), key=f"{page_key}_date_fim")
        filters["data_inicio"] = data_ini
        filters["data_fim"] = data_fim
    else:
        ini, fim = _resolve_date_range(periodo)
        filters["data_inicio"] = ini
        filters["data_fim"] = fim
        
    st.sidebar.caption(f"Período: {filters['data_inicio'].strftime('%d/%m/%Y')} a {filters['data_fim'].strftime('%d/%m/%Y')}")
    return filters


# ── FILTROS ESPECÍFICOS POR PÁGINA ──────────────────────────────────────────

def dashboard_filters():
    """Filtros para o Dashboard Geral (apenas data)."""
    st.sidebar.title("Filtros Dashboard")
    filters = _render_date_filter("dash")
    return filters


def financeiro_filters():
    """Filtros para o Financeiro (apenas data)."""
    st.sidebar.title("Filtros Financeiro")
    filters = _render_date_filter("fin")
    return filters


def pedidos_filters():
    """Filtros para a página de Pedidos (data + status + pagamento)."""
    st.sidebar.title("Filtros Pedidos")
    filters = _render_date_filter("ped")
    
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Detalhes do Pedido")
    
    status_key = "ped_status"
    if status_key not in st.session_state:
        st.session_state[status_key] = "Todos"
    filters["status"] = st.sidebar.selectbox("Status", STATUS_PEDIDOS, key=status_key)
    
    pag_key = "ped_pagamento"
    if pag_key not in st.session_state:
        st.session_state[pag_key] = "Todas"
    filters["pagamento"] = st.sidebar.selectbox(
        "Forma de Pagamento",
        ["Todas", "pix", "cartão", "dinheiro", "crédito", "débito"],
        key=pag_key
    )
    return filters


def produtos_filters():
    """Filtros para a página de Produtos (apenas data por enquanto)."""
    st.sidebar.title("Filtros Produtos")
    filters = _render_date_filter("prod")
    return filters


def clientes_filters():
    """Filtros para a página de Clientes/Usuários."""
    st.sidebar.title("Filtros Clientes")
    filters = _render_date_filter("cli")
    return filters


# ── AUXILIARES DE APLICAÇÃO DE FILTRO ───────────────────────────────────────

def apply_date_filter(df, filters, date_col="createdAt"):
    """Aplica o filtro de período a um DataFrame com coluna de data."""
    if df is None or df.empty or date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = df[date_col].apply(
        lambda x: x.date() if hasattr(x, "date") else x
    )

    ini = filters.get("data_inicio")
    fim = filters.get("data_fim")
    if ini:
        df = df[df[date_col] >= ini]
    if fim:
        df = df[df[date_col] <= fim]
    return df


def apply_status_filter(df, filters, col="status"):
    """Aplica o filtro de status se não for 'Todos'."""
    if df is None or df.empty:
        return df
    status = filters.get("status", "Todos")
    if status != "Todos" and col in df.columns:
        df = df[df[col] == status]
    return df


def apply_payment_filter(df, filters, col="paymentMethod"):
    """Aplica o filtro de forma de pagamento."""
    if df is None or df.empty:
        return df
    pag = filters.get("pagamento", "Todas")
    if pag != "Todas" and col in df.columns:
        df = df[df[col].str.lower() == pag.lower()]
    return df
