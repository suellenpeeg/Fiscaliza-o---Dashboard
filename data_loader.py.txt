import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Nome da ABA que será transformada em dashboard
ABA_DASHBOARD = "CONTROLE - B. DADOS"

@st.cache_data(ttl=300)
def load_data():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)

    # 🔹 Abre o ARQUIVO (planilha inteira)
    spreadsheet = client.open_by_url(st.secrets["sheet_url"])

    # 🔹 Seleciona a ABA específica
    worksheet = spreadsheet.worksheet(ABA_DASHBOARD)

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    return df.fillna(0)
