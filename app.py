from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from dados_loader import carregar_dados_covid

df = carregar_dados_covid()
paises = df["location"].unique()

app = Dash(__name__)
app.title = "Dashboard COVID-19"

app.layout = html.Div([
    html.Div("Análise Interativa da Pandemia de COVID-19", className="navbar"),
    html.Div(className="top-space"),

    html.H1("Dashboard COVID-19", className="titulo"),

    dcc.Dropdown(
        id="pais-dropdown",
        options=[{"label": p, "value": p} for p in paises],
        value="Brazil",
        className="dropdown"
    ),


    html.Div(id="cards-container", className="card-container"),


    dcc.Tabs(
        id="tabs",
        value="tab-casos",
        className="tabs-container",
        children=[
            dcc.Tab(label="Casos", value="tab-casos"),
            dcc.Tab(label="Óbitos", value="tab-obitos"),
            dcc.Tab(label="Visão Geral", value="tab-overview"),
        ]
    ),


    html.Div(id="conteudo-tab", className="tab-content"),

    html.Div("Desenvolvido por você — Dashboard COVID-19", className="footer")
])


@app.callback(
    Output("conteudo-tab", "children"),
    [Input("tabs", "value"),
     Input("pais-dropdown", "value")]
)
def atualizar_tabs(tab, pais):
    dff = df[df["location"] == pais].copy()

    dff["new_cases"] = dff["new_cases"].clip(lower=0)
    dff["new_deaths"] = dff["new_deaths"].clip(lower=0)

    dff["casos_mm7"] = dff["new_cases"].rolling(7).mean()
    dff["mortes_mm7"] = dff["new_deaths"].rolling(7).mean()

    ultimo = dff.iloc[-1]
    total_casos = int(ultimo["total_cases"]) if pd.notna(ultimo["total_cases"]) else 0
    total_mortes = int(ultimo["total_deaths"]) if pd.notna(ultimo["total_deaths"]) else 0

    if tab == "tab-overview":
        if total_casos > 0:
            letalidade = f"{round((total_mortes / total_casos) * 100, 2)}%"
        else:
            letalidade = "N/A"
        return html.Div([
            html.Div([
                html.Div(f"Casos Totais: {total_casos:,}".replace(",", "."), className="card"),
                html.Div(f"Mortes Totais: {total_mortes:,}".replace(",", "."), className="card"),
                html.Div(f"Letalidade: {letalidade}", className="card"),
            ], className="card-container")
        ])

    if tab == "tab-casos":
        fig_casos = px.line(
            dff, x="date", y="casos_mm7",
            template="plotly_dark",
            title=f"Casos (média móvel 7 dias) — {pais}"
        )
        fig_casos.update_layout(height=500)

        return html.Div([
            dcc.Graph(figure=fig_casos)
        ])

    if tab == "tab-obitos":
        fig_obitos = px.line(
            dff, x="date", y="mortes_mm7",
            template="plotly_dark",
            title=f"Óbitos (média móvel 7 dias) — {pais}"
        )
        fig_obitos.update_layout(height=500)

        return html.Div([
            dcc.Graph(figure=fig_obitos)
        ])


if __name__ == "__main__":
    app.run(debug=True)
