import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pptx import Presentation
from pptx.util import Inches
import plotly.express as px
import tempfile

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard Fiscalização 2026",
    layout="wide"
)

ABA_DASHBOARD = "CONTROLE - B. DADOS"

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================

@st.cache_data(ttl=300)
def load_data():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(st.secrets["sheet_url"])
    worksheet = spreadsheet.worksheet(ABA_DASHBOARD)

    data = worksheet.get_all_values()

    df = pd.DataFrame(data[1:], columns=data[0])

    # Remove colunas vazias
    df = df.loc[:, df.columns.notna()]
    df = df.loc[:, df.columns != ""]

    # Tenta converter números
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df


# ==========================================
# EXPORTAÇÃO POWERPOINT
# ==========================================

def gerar_ppt(df, total_geral):

    prs = Presentation()
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = "Relatório Executivo - Fiscalização 2026"

    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(4)

    rows, cols = df.shape

    table = slide.shapes.add_table(
        min(rows + 1, 15),
        cols,
        left,
        top,
        width,
        height
    ).table

    for col in range(cols):
        table.cell(0, col).text = str(df.columns[col])

    for row in range(min(rows, 14)):
        for col in range(cols):
            table.cell(row + 1, col).text = str(df.iloc[row, col])

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    prs.save(temp.name)

    return temp.name


# ==========================================
# APP
# ==========================================

st.title("📊 Dashboard Executivo - Fiscalização 2026")

df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# ==========================================
# IDENTIFICA COLUNAS NUMÉRICAS
# ==========================================

numeric_cols = df.select_dtypes(include="number").columns

# ==========================================
# KPI PRINCIPAL
# ==========================================

total_geral = df[numeric_cols].sum().sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Geral de Ações", int(total_geral))
col2.metric("Dias Registrados", len(df))
col3.metric("Tipos de Indicadores", len(numeric_cols))

st.divider()

# ==========================================
# EVOLUÇÃO DIÁRIA CONSOLIDADA
# ==========================================

df["TOTAL_DIA"] = df[numeric_cols].sum(axis=1)

fig_evolucao = px.line(
    df,
    y="TOTAL_DIA",
    title="Evolução Diária de Ações",
    markers=True
)

st.plotly_chart(fig_evolucao, use_container_width=True)

st.divider()

# ==========================================
# TOTAL POR TIPO (RANKING)
# ==========================================

totais_por_tipo = df[numeric_cols].sum().sort_values(ascending=False)

fig_ranking = px.bar(
    x=totais_por_tipo.values,
    y=totais_por_tipo.index,
    orientation="h",
    title="Ranking por Tipo de Ação"
)

st.plotly_chart(fig_ranking, use_container_width=True)

st.divider()

# ==========================================
# PARTICIPAÇÃO PERCENTUAL
# ==========================================

fig_pizza = px.pie(
    values=totais_por_tipo.values,
    names=totais_por_tipo.index,
    title="Participação Percentual por Tipo"
)

st.plotly_chart(fig_pizza, use_container_width=True)

st.divider()

# ==========================================
# TABELA COMPLETA
# ==========================================

st.subheader("Base Completa")
st.dataframe(df, use_container_width=True)

st.divider()

# ==========================================
# EXPORTAÇÃO
# ==========================================

if st.button("📥 Exportar Relatório em PowerPoint"):

    ppt_file = gerar_ppt(df, total_geral)

    with open(ppt_file, "rb") as f:
        st.download_button(
            "Baixar PowerPoint",
            f,
            file_name="relatorio_fiscalizacao_2026.pptx"
        )





