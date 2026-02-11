import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Executivo - Fiscalização 2026",
    layout="wide"
)

ABA_DASHBOARD = "CONTROLE - B. DADOS"

# =====================================================
# FUNÇÃO ULTRA ESTÁVEL PARA SUA PLANILHA
# =====================================================

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

    if len(data) < 3:
        return pd.DataFrame()

    # Cabeçalhos
    header_grupo = data[0]
    header_sub = data[1]

    colunas = []
    for g, s in zip(header_grupo, header_sub):
        g = g.strip()
        s = s.strip()

        if g and s:
            colunas.append(f"{g} - {s}")
        elif g:
            colunas.append(g)
        else:
            colunas.append(s)

    # Dados reais
    df = pd.DataFrame(data[2:], columns=colunas)

    # Remove as 3 primeiras colunas (DATA / DIA / MÊS)
    df = df.iloc[:, 3:]

    # Converte TUDO para número de forma segura
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove colunas totalmente vazias
    df = df.dropna(axis=1, how="all")

    return df.fillna(0)


# =====================================================
# APP
# =====================================================

st.title("📊 Dashboard Executivo - Fiscalização 2026")

df = load_data()

if df.empty:
    st.warning("Não foi possível carregar dados da planilha.")
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns

if len(numeric_cols) == 0:
    st.warning("Nenhuma coluna numérica encontrada.")
    st.stop()

# =====================================================
# KPIs
# =====================================================

total_geral = df[numeric_cols].sum().sum()

col1, col2 = st.columns(2)

col1.metric("Total Geral de Ações", int(total_geral))
col2.metric("Indicadores Monitorados", len(numeric_cols))

st.divider()

# =====================================================
# EVOLUÇÃO
# =====================================================

df["TOTAL_DIA"] = df[numeric_cols].sum(axis=1)

fig_evolucao = px.line(
    df,
    y="TOTAL_DIA",
    title="Evolução Diária Consolidada",
    markers=True
)

st.plotly_chart(fig_evolucao, use_container_width=True)

st.divider()

# =====================================================
# RANKING
# =====================================================

totais_por_tipo = df[numeric_cols].sum().sort_values(ascending=False)

df_rank = totais_por_tipo.reset_index()
df_rank.columns = ["Indicador", "Total"]

fig_rank = px.bar(
    df_rank,
    x="Total",
    y="Indicador",
    orientation="h",
    title="Ranking por Tipo de Ação"
)

st.plotly_chart(fig_rank, use_container_width=True)

st.divider()

# =====================================================
# PARTICIPAÇÃO
# =====================================================

fig_pizza = px.pie(
    df_rank,
    values="Total",
    names="Indicador",
    title="Participação Percentual"
)

st.plotly_chart(fig_pizza, use_container_width=True)
