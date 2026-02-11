import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(page_title="Dashboard Fiscalização", layout="wide")

ABA = "BANCO DE DADOS"


# =====================================================
# LOAD DATA ROBUSTO
# =====================================================

@st.cache_data(ttl=300)
def load_data():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(st.secrets["sheet_url"])
    worksheet = spreadsheet.worksheet(ABA)

    data = worksheet.get_all_values()

    # Remove linhas totalmente vazias
    data = [row for row in data if any(cell.strip() != "" for cell in row)]

    # 🔎 Detecta automaticamente linha de cabeçalho
    header_index = None
    for i, row in enumerate(data):
        row_upper = [cell.strip().upper() for cell in row]
        if "TIPOLOGIA" in row_upper:
            header_index = i
            break

    if header_index is None:
        st.error("Não foi possível localizar a linha de cabeçalho.")
        st.stop()

    header = [col.strip().upper() for col in data[header_index]]

    df = pd.DataFrame(data[header_index + 1:], columns=header)

    return df


# =====================================================
# APP
# =====================================================

st.title("📊 Dashboard Executivo - Fiscalização")

df = load_data()

if df.empty:
    st.warning("Sem dados válidos.")
    st.stop()

# 🔧 Garante colunas essenciais
colunas_necessarias = ["TIPOLOGIA", "BAIRRO", "DATA"]

for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"Coluna obrigatória não encontrada: {col}")
        st.write("Colunas encontradas:", df.columns)
        st.stop()

# Converte DATA
df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")

df = df.dropna(subset=["DATA"])

# =====================================================
# KPIs
# =====================================================

total = len(df)

tipo_top = df["TIPOLOGIA"].value_counts().idxmax()
bairro_top = df["BAIRRO"].value_counts().idxmax()

c1, c2, c3 = st.columns(3)

c1.metric("Total de Ocorrências", total)
c2.metric("Tipologia Mais Frequente", tipo_top)
c3.metric("Bairro com Mais Registros", bairro_top)

st.divider()

# =====================================================
# EVOLUÇÃO
# =====================================================

evolucao = df.groupby("DATA").size().reset_index(name="Total")

fig1 = px.line(
    evolucao,
    x="DATA",
    y="Total",
    markers=True,
    title="Evolução de Ocorrências"
)

fig1.update_layout(plot_bgcolor="white")

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# =====================================================
# RANKING TIPOLOGIA
# =====================================================

ranking_tipo = df["TIPOLOGIA"].value_counts().reset_index()
ranking_tipo.columns = ["Tipologia", "Total"]

fig2 = px.bar(
    ranking_tipo,
    x="Total",
    y="Tipologia",
    orientation="h",
    title="Ranking por Tipologia"
)

fig2.update_layout(plot_bgcolor="white")

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# =====================================================
# TOP BAIRROS
# =====================================================

ranking_bairro = df["BAIRRO"].value_counts().head(10).reset_index()
ranking_bairro.columns = ["Bairro", "Total"]

fig3 = px.bar(
    ranking_bairro,
    x="Total",
    y="Bairro",
    orientation="h",
    title="Top 10 Bairros"
)

fig3.update_layout(plot_bgcolor="white")

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# =====================================================
# MAPA (se tiver coordenadas)
# =====================================================

if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:

    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

    df_map = df.dropna(subset=["LATITUDE", "LONGITUDE"])

    if not df_map.empty:

        fig4 = px.scatter_mapbox(
            df_map,
            lat="LATITUDE",
            lon="LONGITUDE",
            color="TIPOLOGIA",
            zoom=12,
            height=500
        )

        fig4.update_layout(mapbox_style="open-street-map")

        st.plotly_chart(fig4, use_container_width=True)




