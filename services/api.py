import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from services.firebase_client import get_firestore_client


# ─────────────────────────────────────────
# HELPERS INTERNOS (sem cache – usados pelos métodos públicos)
# ─────────────────────────────────────────

def _fetch_orders():
    """Busca todos os pedidos da coleção 'orders' com dados completos."""
    db = get_firestore_client()
    docs = db.collection('orders').get()
    rows = []
    for doc in docs:
        d = doc.to_dict()
        created = d.get('createdAt')
        if created and hasattr(created, 'timestamp'):
            created = datetime.fromtimestamp(created.timestamp())

        # Extrai itens do pedido
        items = d.get('items', [])
        itens_desc = ", ".join(
            f"{it.get('name','?')} (x{it.get('quantity',1)})"
            for it in items
        ) if items else "—"
        qtd_itens = sum(it.get('quantity', 1) for it in items) if items else 0

        # Dados do cliente
        customer = d.get('customerData', {}) or {}

        rows.append({
            'id': doc.id,
            'createdAt': created,
            'Data': created.date() if created else None,
            'Hora': created.strftime('%H:%M') if created else '—',
            'status': d.get('status', 'pendente'),
            'Status': d.get('status', 'pendente'),
            'totalWithFrete': float(d.get('totalWithFrete', 0) or 0),
            'Frete (R$)': float(d.get('freteValue', 0) or 0),
            'Subtotal (R$)': float(d.get('totalWithFrete', 0) or 0) - float(d.get('freteValue', 0) or 0),
            'Total (R$)': float(d.get('totalWithFrete', 0) or 0),
            'paymentMethod': d.get('paymentMethod', ''),
            'Pagamento': d.get('paymentMethod', '—'),
            'deliveryType': d.get('deliveryType', ''),
            'Entrega': d.get('deliveryType', '—'),
            'orderRef': d.get('orderRef', doc.id[:8]),
            'Ref.': d.get('orderRef', doc.id[:8]),
            'Cliente': customer.get('name') or customer.get('nome', '—'),
            'Itens': itens_desc,
            'Qtd Itens': qtd_itens,
        })
    return pd.DataFrame(rows)


def _fetch_vendas():
    """Busca todas as vendas da coleção 'vendas'."""
    db = get_firestore_client()
    docs = db.collection('vendas').get()
    rows = []
    for doc in docs:
        d = doc.to_dict()
        created = d.get('created_at') or d.get('criadoEm') or d.get('dataVenda')
        if created and hasattr(created, 'timestamp'):
            created = datetime.fromtimestamp(created.timestamp())
        rows.append({
            'id': doc.id,
            'createdAt': created,
            'status': d.get('status', 'pendente'),
            'valor_total': float(d.get('valor_total') or d.get('total', 0) or 0),
            'subtotal': float(d.get('subtotal', 0) or 0),
            'desconto': float(d.get('desconto', 0) or 0),
            'forma_pagamento': d.get('forma_pagamento') or d.get('formaPagamento', ''),
            'cliente_nome': d.get('cliente_nome') or d.get('clienteNome', ''),
        })
    return pd.DataFrame(rows)


def _fetch_clients():
    """Busca todos os clientes da coleção 'clients'."""
    db = get_firestore_client()
    docs = db.collection('clients').get()
    rows = []
    for doc in docs:
        d = doc.to_dict()
        created = d.get('criadoEm')
        if created and hasattr(created, 'timestamp'):
            created = datetime.fromtimestamp(created.timestamp())
        rows.append({
            'id': doc.id,
            'nome': d.get('nome', ''),
            'email': d.get('email', ''),
            'telefone': d.get('telefone', ''),
            'criadoEm': created,
        })
    return pd.DataFrame(rows)


def _fetch_produtos():
    """Busca todos os produtos da coleção 'produtos'."""
    db = get_firestore_client()
    docs = db.collection('produtos').get()
    rows = []
    for doc in docs:
        d = doc.to_dict()
        rows.append({
            'id': doc.id,
            'nome': d.get('nome') or d.get('name', ''),
            'preco': float(d.get('preco') or d.get('price', 0) or 0),
            'precoPromocional': float(d.get('precoPromocional', 0) or 0),
            'estoque': int(d.get('estoque', 0) or 0),
            'categoria': d.get('categoria') or d.get('category', ''),
            'ativo': d.get('ativo', True),
            'imageUrl': d.get('imageUrl') or d.get('urlImagem', ''),
            'sku': d.get('sku', ''),
        })
    return pd.DataFrame(rows)


def _build_vendas_por_produto():
    """Agrega quantidade vendida por nome de produto cruzando todos os pedidos."""
    db = get_firestore_client()
    docs = db.collection('orders').get()
    sales: dict = {}  # nome -> {qtd, receita}
    for doc in docs:
        items = doc.to_dict().get('items', []) or []
        for item in items:
            nome = item.get('name') or item.get('nome', 'Desconhecido')
            qtd  = int(item.get('quantity', 1) or 1)
            val  = float(item.get('totalPrice') or item.get('unitPrice', 0) or 0) * qtd
            if nome not in sales:
                sales[nome] = {'Qtd Vendida': 0, 'Receita Vendas (R$)': 0.0}
            sales[nome]['Qtd Vendida']        += qtd
            sales[nome]['Receita Vendas (R$)'] += val
    if not sales:
        return pd.DataFrame()
    df = pd.DataFrame([
        {'nome': k, 'Qtd Vendida': v['Qtd Vendida'], 'Receita Vendas (R$)': v['Receita Vendas (R$)']}
        for k, v in sales.items()
    ])
    return df


def _fetch_vendedores():
    """Busca todos os vendedores."""
    db = get_firestore_client()
    docs = db.collection('vendedores').get()
    rows = []
    for doc in docs:
        d = doc.to_dict()
        rows.append({
            'id': doc.id,
            'nome': d.get('nome', ''),
            'email': d.get('email', ''),
            'comissao': float(d.get('comissao', 0) or 0),
            'metaVendas': float(d.get('metaVendas', 0) or 0),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────

def _apply_date_filter(df, filters, date_col='createdAt'):
    """Auxiliar para filtrar DataFrames por data com base no filtro global."""
    if df is None or df.empty or not filters:
        return df
    ini = filters.get('data_inicio')
    fim = filters.get('data_fim')
    if not ini and not fim:
        return df
    df = df.copy()
    df['temp_date'] = df[date_col].apply(lambda x: x.date() if hasattr(x, 'date') and x is not None else x)
    if ini:
        df = df[df['temp_date'] >= ini]
    if fim:
        df = df[df['temp_date'] <= fim]
    df = df.drop(columns=['temp_date'])
    return df


@st.cache_data(ttl=600)
def get_dashboard_summary(filters=None):
    """Retorna KPIs gerais combinando orders + vendas + clients + produtos com filtros aplicados."""
    try:
        orders = _fetch_orders()
        vendas = _fetch_vendas()
        clients = _fetch_clients()
        produtos = _fetch_produtos()

        # Filtra por data
        if filters:
            orders = _apply_date_filter(orders, filters, 'createdAt')
            vendas = _apply_date_filter(vendas, filters, 'createdAt')

        receita_orders = orders['totalWithFrete'].sum() if not orders.empty else 0
        receita_vendas = vendas['valor_total'].sum() if not vendas.empty else 0
        receita_total = receita_orders + receita_vendas

        total_ops = len(orders) + len(vendas)
        ticket_medio = receita_total / total_ops if total_ops > 0 else 0

        return {
            "total_users": len(clients),
            "active_users": len(clients),
            "new_users": 0,
            "revenue": receita_total,
            "avg_ticket": ticket_medio,
            "operations": total_ops,
            "avg_response_time": "—",
            "growth": 0.0,
            "total_produtos": len(produtos),
            "produtos_ativos": int(produtos['ativo'].sum()) if not produtos.empty else 0,
        }
    except Exception as e:
        st.warning("Erro ao carregar resumo: " + str(e))
        return {
            "total_users": 0, "active_users": 0, "new_users": 0,
            "revenue": 0.0, "avg_ticket": 0.0, "operations": 0,
            "avg_response_time": "—", "growth": 0.0,
            "total_produtos": 0, "produtos_ativos": 0,
        }


@st.cache_data(ttl=600)
def get_revenue_data(filters=None):
    """
    Série temporal de receita separando produtos x frete (com filtros de data).
    """
    try:
        orders    = _fetch_orders()
        vendas    = _fetch_vendas()
        vendedores = _fetch_vendedores()

        # Aplica filtros de data
        if filters:
            orders = _apply_date_filter(orders, filters, 'createdAt')
            vendas = _apply_date_filter(vendas, filters, 'createdAt')

        # Comissão média real
        if not vendedores.empty and vendedores['comissao'].sum() > 0:
            comissao_media = vendedores['comissao'].mean() / 100.0
        else:
            comissao_media = 0.10  # fallback 10%

        frames = []

        if not orders.empty:
            o = orders.dropna(subset=['createdAt']).copy()
            o['Data'] = o['createdAt'].dt.date
            agg = o.groupby('Data').agg(
                Receita=('totalWithFrete', 'sum'),
                Frete_Cobrado=('Frete (R$)', 'sum'),
            ).reset_index()
            # Receita de produtos = total - frete (frete é repasse, não receita da loja)
            agg['Receita_Produtos'] = agg['Receita'] - agg['Frete_Cobrado']
            frames.append(agg)

        if not vendas.empty:
            v = vendas.dropna(subset=['createdAt']).copy()
            v['Data'] = v['createdAt'].dt.date
            agg_v = v.groupby('Data').agg(
                Receita=('valor_total', 'sum'),
            ).reset_index()
            agg_v['Frete_Cobrado']   = 0.0
            agg_v['Receita_Produtos'] = agg_v['Receita']
            frames.append(agg_v)

        if not frames:
            return pd.DataFrame({
                'Data': [], 'Receita': [], 'Receita_Produtos': [],
                'Frete_Cobrado': [], 'Custos': [], 'Lucro': [], 'comissao_media': []
            })

        combined = (
            pd.concat(frames)
            .groupby('Data')
            .agg(Receita=('Receita', 'sum'),
                 Receita_Produtos=('Receita_Produtos', 'sum'),
                 Frete_Cobrado=('Frete_Cobrado', 'sum'))
            .reset_index()
        )

        # Custo = comissão sobre a receita de produtos (frete não entra como despesa)
        combined['Custos']          = combined['Receita_Produtos'] * comissao_media
        combined['Lucro']           = combined['Receita_Produtos'] - combined['Custos']
        combined['comissao_media']  = comissao_media
        return combined.sort_values('Data')

    except Exception as e:
        st.warning("Erro ao carregar receitas: " + str(e))
        return pd.DataFrame({
            'Data': [], 'Receita': [], 'Receita_Produtos': [],
            'Frete_Cobrado': [], 'Custos': [], 'Lucro': [], 'comissao_media': []
        })


@st.cache_data(ttl=600)
def get_users_data(filters=None):
    """Retorna dados dos clientes."""
    try:
        clients = _fetch_clients()
        if clients.empty:
            return pd.DataFrame({"Status": ["Sem dados"], "Quantidade": [0]})
        return clients
    except Exception as e:
        return pd.DataFrame({"Status": ["Erro"], "Quantidade": [0]})


@st.cache_data(ttl=600)
def get_products_ranking(filters=None):
    """Retorna ranking de produtos por preço."""
    try:
        produtos = _fetch_produtos()
        if produtos.empty:
            return pd.DataFrame({'Produto': [], 'Preco': [], 'Estoque': []})
        df = produtos[produtos['ativo'] == True][['nome', 'preco', 'precoPromocional', 'estoque', 'categoria']]
        df = df.rename(columns={'nome': 'Produto', 'preco': 'Preco', 'estoque': 'Estoque', 'categoria': 'Categoria'})
        return df.sort_values('Preco', ascending=False).head(20)
    except Exception as e:
        return pd.DataFrame({'Produto': [], 'Preco': [], 'Estoque': []})


@st.cache_data(ttl=600)
def get_vendedores_data(filters=None):
    """Retorna dados dos vendedores."""
    try:
        return _fetch_vendedores()
    except Exception:
        return pd.DataFrame({'nome': [], 'email': [], 'comissao': [], 'metaVendas': []})


@st.cache_data(ttl=600)
def get_system_performance(filters=None):
    """Performance simulada (não há coleção de logs no Firebase)."""
    times = pd.date_range(end=datetime.today(), periods=24, freq='h')
    return pd.DataFrame({
        "Hora": times,
        "Latência (ms)": np.random.normal(150, 30, 24).round(0),
        "Erros": np.random.poisson(2, 24)
    })


@st.cache_data(ttl=300)
def get_pedidos_detalhados():
    """Retorna todos os pedidos detalhados sem cache longo (refresh a cada 5 min)."""
    try:
        return _fetch_orders()
    except Exception as e:
        st.warning("Erro ao carregar pedidos: " + str(e))
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_produtos_com_vendas():
    """
    Retorna DataFrame de produtos enriquecido com quantidade vendida real,
    cruzando a coleção 'produtos' com os itens de 'orders'.
    Colunas: nome, preco, precoPromocional, estoque, categoria, ativo, imageUrl,
             Qtd Vendida, Receita Vendas (R$)
    """
    try:
        produtos = _fetch_produtos()
        vendas   = _build_vendas_por_produto()

        if produtos.empty:
            return pd.DataFrame()

        if vendas.empty:
            produtos['Qtd Vendida']        = 0
            produtos['Receita Vendas (R$)'] = 0.0
            return produtos

        merged = produtos.merge(vendas, on='nome', how='left')
        merged['Qtd Vendida']        = merged['Qtd Vendida'].fillna(0).astype(int)
        merged['Receita Vendas (R$)'] = merged['Receita Vendas (R$)'].fillna(0.0)
        return merged
    except Exception as e:
        st.warning("Erro ao carregar produtos com vendas: " + str(e))
        return pd.DataFrame()
