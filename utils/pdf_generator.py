"""
Gerador de relatórios PDF usando ReportLab.
Exporta tabelas e KPIs de qualquer DataFrame do Streamlit Analytics.
"""
import io
import pandas as pd
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Paleta de cores da marca ────────────────────────────────────────────────
COR_PRIMARIA   = colors.HexColor("#1B4F72")   # Azul escuro
COR_SECUNDARIA = colors.HexColor("#2E86AB")   # Azul médio
COR_ACENTO     = colors.HexColor("#F39C12")   # Laranja
COR_CLARO      = colors.HexColor("#EBF5FB")   # Azul muito claro
COR_LINHA_PAR  = colors.HexColor("#F8F9FA")   # Cinza claro
COR_TEXTO      = colors.HexColor("#2C3E50")   # Cinza escuro

STYLES = getSampleStyleSheet()

STYLE_TITULO = ParagraphStyle(
    "Titulo",
    parent=STYLES["Heading1"],
    fontSize=20,
    textColor=COR_PRIMARIA,
    spaceAfter=4,
    fontName="Helvetica-Bold",
    alignment=TA_LEFT,
)
STYLE_SUBTITULO = ParagraphStyle(
    "Subtitulo",
    parent=STYLES["Normal"],
    fontSize=10,
    textColor=COR_SECUNDARIA,
    spaceAfter=2,
    fontName="Helvetica",
)
STYLE_SECAO = ParagraphStyle(
    "Secao",
    parent=STYLES["Heading2"],
    fontSize=13,
    textColor=COR_PRIMARIA,
    spaceBefore=14,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)
STYLE_RODAPE = ParagraphStyle(
    "Rodape",
    parent=STYLES["Normal"],
    fontSize=8,
    textColor=colors.grey,
    alignment=TA_CENTER,
)
STYLE_KPI_LABEL = ParagraphStyle(
    "KpiLabel",
    parent=STYLES["Normal"],
    fontSize=9,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    alignment=TA_CENTER,
)
STYLE_KPI_VALUE = ParagraphStyle(
    "KpiValue",
    parent=STYLES["Normal"],
    fontSize=14,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    alignment=TA_CENTER,
)


def _build_kpi_table(kpis: list[dict]) -> Table:
    """
    Constrói uma tabela de KPIs no topo do PDF.
    kpis = [{"label": "Receita", "value": "R$ 1.200,00"}, ...]
    """
    headers = [Paragraph(k["label"], STYLE_KPI_LABEL) for k in kpis]
    values  = [Paragraph(k["value"],  STYLE_KPI_VALUE) for k in kpis]

    col_w = (A4[0] - 3 * cm) / len(kpis)
    t = Table([headers, values], colWidths=[col_w] * len(kpis), rowHeights=[18, 26])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), COR_SECUNDARIA),
        ("BACKGROUND",  (0, 0), (-1, 0),  COR_PRIMARIA),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.white),
    ]))
    return t


def _format_cell(v) -> str:
    """Formata um valor de célula para exibição no PDF."""
    import datetime as dt
    if v is None:
        return "—"
    if isinstance(v, (dt.date, dt.datetime)):
        return v.strftime("%d/%m/%Y")
    return str(v)


def _build_data_table(df, max_rows: int = 500) -> Table:
    """Converte um DataFrame em uma Table ReportLab estilizada."""
    import datetime as dt
    df = df.head(max_rows).copy()

    # Converte colunas de data para string formatada DD/MM/YYYY
    for col in df.columns:
        if df[col].dtype == 'object':
            pass  # já string
        else:
            sample = df[col].dropna().head(1)
            if len(sample) > 0 and isinstance(sample.iloc[0], (dt.date, dt.datetime)):
                df[col] = df[col].apply(
                    lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) and x is not None else "—"
                )

    cols = list(df.columns)

    # Calcula largura proporcional das colunas
    page_w = landscape(A4)[0] - 3 * cm
    col_w  = page_w / len(cols)

    header_style = ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8,
        textColor=colors.white, alignment=TA_CENTER
    )
    cell_style = ParagraphStyle(
        "td", fontName="Helvetica", fontSize=7.5,
        textColor=COR_TEXTO, alignment=TA_LEFT
    )

    header_row = [Paragraph(str(c), header_style) for c in cols]
    data_rows  = [
        [Paragraph(_format_cell(v), cell_style) for v in row]
        for row in df.itertuples(index=False)
    ]

    table_data = [header_row] + data_rows
    t = Table(table_data, colWidths=[col_w] * len(cols), repeatRows=1)

    style_cmds = [
        ("BACKGROUND",    (0, 0),  (-1, 0),  COR_PRIMARIA),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0),  (-1, 0),  8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_LINHA_PAR]),
        ("GRID",          (0, 0),  (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0),  (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 4),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 5),
        ("VALIGN",        (0, 0),  (-1, -1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def gerar_pdf(
    titulo: str,
    subtitulo: str,
    df,
    kpis: list[dict] | None = None,
    secao_tabela: str = "Dados Detalhados",
    orientacao: str = "landscape",   # "portrait" ou "landscape"
    max_rows: int = 500,
) -> bytes:
    """
    Gera o PDF em memória e retorna bytes para o st.download_button.

    Parâmetros:
        titulo        – Título principal do relatório
        subtitulo     – Subtítulo / período
        df            – DataFrame com os dados
        kpis          – Lista de dicts {"label": ..., "value": ...}
        secao_tabela  – Título da seção da tabela
        orientacao    – "landscape" ou "portrait"
        max_rows      – Limite de linhas exportadas
    """
    buffer = io.BytesIO()
    pagesize = landscape(A4) if orientacao == "landscape" else A4
    margins = dict(leftMargin=1.5*cm, rightMargin=1.5*cm,
                   topMargin=1.5*cm, bottomMargin=1.5*cm)

    doc = SimpleDocTemplate(buffer, pagesize=pagesize, **margins)

    from datetime import datetime
    hoje_fmt = datetime.now().strftime("%d/%m/%Y às %H:%M")

    story = []

    # ── Cabeçalho ──────────────────────────────────────────────────────
    story.append(Paragraph("Dellas — Analytics BI", STYLE_SUBTITULO))
    story.append(Paragraph(titulo, STYLE_TITULO))
    story.append(Paragraph(subtitulo, STYLE_SUBTITULO))

    # Data de geração em destaque
    data_style = ParagraphStyle(
        "DataGeracao",
        parent=STYLES["Normal"],
        fontSize=9,
        textColor=COR_ACENTO,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    story.append(Paragraph(f"Gerado em: {hoje_fmt}", data_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COR_ACENTO, spaceAfter=10))

    # ── KPIs ───────────────────────────────────────────────────────────
    if kpis:
        story.append(Paragraph("Resumo Executivo", STYLE_SECAO))
        story.append(_build_kpi_table(kpis))
        story.append(Spacer(1, 14))

    # ── Tabela de dados ────────────────────────────────────────────────
    if df is not None and not df.empty:
        story.append(Paragraph(secao_tabela, STYLE_SECAO))
        story.append(Spacer(1, 4))
        story.append(_build_data_table(df, max_rows=max_rows))

    # ── Rodapé ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Gerado em {date.today().strftime('%d/%m/%Y')} — Dellas Analytics BI  |  Confidencial",
        STYLE_RODAPE
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
