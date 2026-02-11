import plotly.express as px
import pandas as pd

def chart_totais_por_tipo(df):

    totais = {}

    for col in df.columns:
        if "AÇÕES" in col:
            totais[col] = df[col].sum()

    df_plot = pd.DataFrame({
        "Tipo": totais.keys(),
        "Total": totais.values()
    })

    fig = px.bar(
        df_plot,
        x="Tipo",
        y="Total",
        text="Total",
        color="Total",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Total de Ações por Tipo",
        template="plotly_white"
    )

    return fig


def chart_evolucao(df):

    fig = px.line(
        df,
        x="DATA",
        y="TOTAL_ACOES",
        markers=True,
        title="Evolução Diária de Ações"
    )

    fig.update_layout(template="plotly_white")

    return fig
