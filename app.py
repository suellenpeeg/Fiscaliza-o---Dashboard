import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(page_title="Dashboard Fiscalização", layout="wide")

ABA = "B. DE DADOS"


@st.cache_data(ttl=300)

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

    if len(data) < 2:
        return pd.DataFrame()

    # usa primeira linha como cabeçalho real
    header = data[0]
    df = pd.DataFrame(data[1:], columns=header)

    return df


df = load_data()

st.title("📊 Dashboard Executivo - Fiscalização")

if df.empty:
    st.warning("Sem dados.")
    st.stop()

# ========================
# KPIs
# ========================

total = len(df)

tipo_top = df["TIPOLOGIA"].value_counts().idxmax()
bairro_top = df["BAIRRO"].value_counts().idxmax()

c1, c2, c3 = st.columns(3)
c1.metric("Total de Ocorrências", total)
c2.metric("Tipologia Mais Frequente", tipo_top)
c3.metric("Bairro com Mais Registros", bairro_top)

st.divider()

# ========================
# Evolução por Data
# ========================

evolucao = df.groupby("DATA").size().reset_index(name="Total")

fig1 = px.line(
    evolucao,
    x="DATA",
    y="Total",
    markers=True,
    title="Evolução de Ocorrências"
)

st.plotly_chart(fig1, use_container_width=True)

# ========================
# Ranking Tipologia
# ========================

ranking_tipo = df["TIPOLOGIA"].value_counts().reset_index()
ranking_tipo.columns = ["Tipologia", "Total"]

fig2 = px.bar(
    ranking_tipo,
    x="Total",
    y="Tipologia",
    orientation="h",
    title="Ranking por Tipologia"
)

st.plotly_chart(fig2, use_container_width=True)

# ========================
# Ranking Bairro
# ========================

ranking_bairro = df["BAIRRO"].value_counts().reset_index()
ranking_bairro.columns = ["Bairro", "Total"]

fig3 = px.bar(
    ranking_bairro.head(10),
    x="Total",
    y="Bairro",
    orientation="h",
    title="Top 10 Bairros"
)

st.plotly_chart(fig3, use_container_width=True)

# ========================
# MAPA
# ========================

if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:

    df_map = df.dropna(subset=["LATITUDE", "LONGITUDE"])

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




