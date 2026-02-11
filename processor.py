import pandas as pd

def process_data(df):

    col_acoes = [c for c in df.columns if "AÇÕES" in c]
    col_bd = [c for c in df.columns if "B. DADOS" in c]

    df["TOTAL_ACOES"] = df[col_acoes].sum(axis=1)
    df["TOTAL_BD"] = df[col_bd].sum(axis=1)

    df["CONFORMIDADE"] = (
        df["TOTAL_BD"] / df["TOTAL_ACOES"]
    ).replace([float("inf")], 0).fillna(0) * 100

    return df
