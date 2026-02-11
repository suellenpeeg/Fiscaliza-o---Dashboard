import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pptx import Presentation
from pptx.util import Inches
import plotly.express as px
import tempfile

# =============================
# CONFIGURAÇÃO
# =============================

st.set_page_config(
    page_title="Dashboard Fiscalização",
    layout="wide"
)

ABA_DASHBOARD = "CONTROLE - B. DADOS"

# =============================
# CARREGAMENTO DOS DADOS
# =============================

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

    return df


# =============================
# EXPORTAÇÃO POWERPOINT
# =============================

def gerar_ppt(df):

    prs = Presentation()

    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)

    title = slide.shapes.title
    title.text = "Dashboard Fiscalização"

    rows, cols = df.shape

    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(4)

    table = slide.shapes.add_table(
        min(rows+1, 15),
        cols,
        left,
        top,
        width,
        height
    ).table

    # Cabeçalho
    for col in range(cols):
        table.cell(0, col).text = df.columns[col]

    # Dados
    for row in range(min(rows, 14)):
        for col in range(cols):
            table.cell(row+1, col).text = str(df.iloc[row, col])

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    prs.save(temp.name)

    return temp.name


# =============================
# APP
# =============================

st.title("📊 Dashboard Fiscalização")

df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# =============================
# KPIs
# =============================

col1, col2, col3 = st.columns(3)

col1.metric("Total de Registros", len(df))

if "Status" in df.columns:
    col2.metric("Status Únicos", df["Status"].nunique())

col3.metric("Colunas", len(df.columns))

st.divider()

# =============================
# GRÁFICOS AUTOMÁTICOS
# =============================

for col in df.columns:

    if df[col].dtype == "object":

        value_counts = df[col].value_counts().head(10)

        if len(value_counts) > 1:

            fig = px.bar(
                value_counts,
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribuição por {col}"
            )

            st.plotly_chart(fig, use_container_width=True)

# =============================
# TABELA COMPLETA
# =============================

st.subheader("Base Completa")
st.dataframe(df, use_container_width=True)

# =============================
# EXPORTAR PPT
# =============================

if st.button("📥 Exportar para PowerPoint"):

    ppt_file = gerar_ppt(df)

    with open(ppt_file, "rb") as f:
        st.download_button(
            "Baixar PowerPoint",
            f,
            file_name="dashboard_fiscalizacao.pptx"
        )





