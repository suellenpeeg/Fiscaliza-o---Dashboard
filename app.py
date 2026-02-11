import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(page_title="Dashboard Executivo 2026", layout="wide")

ABA_DASHBOARD = "CONTROLE - B. DADOS"

# =====================================================
# FUNÇÃO AUXILIAR
# =====================================================

def make_unique(columns):
    seen = {}
    new_cols = []

    for col in columns:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)

    return new_cols


# =====================================================
# CARGA DE DADOS
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

    header_grupo = data[0]
    header_sub = data[1]

    colunas = []

    for i in range(len(header_grupo)):
        grupo = header_grupo[i].strip()
        sub = header_sub[i].strip()

        if grupo and sub:
            nome = f"{grupo} - {sub}"
        elif grupo:
            nome = grupo
        else:
            nome = sub

        colunas.append(nome)

    colunas = make_unique(colunas)

    df = pd.DataFrame(data[2:], columns=colunas)

    # Mantém DATA (primeira coluna)
    df.rename(columns={df.columns[0]: "DATA"}, inplace=True)

    # Remove colunas texto intermediárias
    df = df.drop(columns=df.columns[1:3])

    # Converte numérico
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.fillna(0)

    return df


# =====================================================
# APP
# =====================================================

st.title("📊 Dashboard Executivo - Fiscalização 2026")

df = load_data()

if df.empty:
    st.warning("Sem dados.")
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns

# =====================================================
# KPI
# =====================================================

df["TOTAL_DIA"] = df[numeric_cols].sum(axis=1)

total_geral = df["TOTAL_DIA"].sum()
dia_max = df.loc[df["TOTAL_DIA"].idxmax(), "DATA"]
valor_max = df["TOTAL_DIA"].max()

acoes_cols = [c for c in numeric_cols if "AÇÕES" in c.upper()]
bd_cols = [c for c in numeric_cols if "B. DADOS" in c.upper()]

total_acoes = df[acoes_cols].sum().sum() if acoes_cols else 0
total_bd = df[bd_cols].sum().sum() if bd_cols else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Geral", int(total_geral))
col2.metric("Total Ações", int(total_acoes))
col3.metric("Total B. Dados", int(total_bd))
col4.metric("Dia mais produtivo", f"{dia_max} ({int(valor_max)})")

st.divider()

# =====================================================
# EVOLUÇÃO
# =====================================================

fig = px.line(
    df,
    x="DATA",
    y="TOTAL_DIA",
    markers=True,
    title="Evolução Diária Consolidada"
)

fig.update_layout(
    plot_bgcolor="white",
    title_font_size=20
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =====================================================
# TOP 5
# =====================================================

totais = df[numeric_cols].sum().sort_values(ascending=False).head(5)
df_rank = totais.reset_index()
df_rank.columns = ["Indicador", "Total"]

fig2 = px.bar(
    df_rank,
    x="Total",
    y="Indicador",
    orientation="h",
    title="Top 5 Indicadores"
)

fig2.update_layout(plot_bgcolor="white")

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# =====================================================
# HEATMAP
# =====================================================

heatmap_df = df[["DATA", "TOTAL_DIA"]]

fig3 = px.imshow(
    [heatmap_df["TOTAL_DIA"].values],
    labels=dict(x="Dias", color="Total"),
    title="Mapa de Intensidade Diária"
)

st.plotly_chart(fig3, use_container_width=True)


