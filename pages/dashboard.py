import dash
from dash import html, dcc, Input, Output
import plotly.express as px
from dados_loader import carregar_dados_covid

dash.register_page(
    __name__,
    path="/dashboard",
    name="Dashboard"
)

df = carregar_dados_covid()

df = df.sort_values("date")

paises = sorted(df["location"].dropna().unique())

layout = html.Div([

    html.H1("Dashboard COVID-19", className="titulo"),

    dcc.Dropdown(
        id="pais-dropdown",
        options=[{"label": p, "value": p} for p in paises],
        value="Brazil",
        className="dropdown"
    ),

    dcc.Tabs(
        id="tabs",
        value="tab-overview",
        children=[
            dcc.Tab(label="Visão Geral", value="tab-overview"),
            dcc.Tab(label="Casos", value="tab-casos"),
            dcc.Tab(label="Óbitos", value="tab-obitos"),
            dcc.Tab(label="Vacinação", value="tab-vacinacao"),
        ]
    ),

    html.Div(id="conteudo-tab")
])

@dash.callback(
    Output("conteudo-tab", "children"),
    Input("tabs", "value"),
    Input("pais-dropdown", "value")
)
def atualizar_tabs(tab, pais):

    dff = df[df["location"] == pais].copy()

    if dff.empty:
        return html.Div("Sem dados disponíveis para este país.", style={"padding": "30px"})


    dff["new_cases"] = dff["new_cases"].fillna(0).clip(lower=0)
    dff["new_deaths"] = dff["new_deaths"].fillna(0).clip(lower=0)

    dff["casos_mm7"] = dff["new_cases"].rolling(7).mean()
    dff["mortes_mm7"] = dff["new_deaths"].rolling(7).mean()

    for col in [
        "people_vaccinated",
        "people_fully_vaccinated",
        "total_vaccinations",
        "population"
    ]:
        if col not in dff.columns:
            dff[col] = 0
        else:
            dff[col] = dff[col].fillna(0)

    total_casos = int(dff["new_cases"].sum())
    total_mortes = int(dff["new_deaths"].sum())

    vacinados = int(dff["people_vaccinated"].max())
    completamente_vacinados = int(dff["people_fully_vaccinated"].max())
    populacao = int(dff["population"].max())

    # Ajustes para inconsistências do OWID
    vacinados = min(vacinados, populacao) if populacao > 0 else vacinados
    completamente_vacinados = min(completamente_vacinados, vacinados)

    nao_vacinados = max(populacao - vacinados, 0) if populacao > 0 else 0

    letalidade = (
        f"{round((total_mortes / total_casos) * 100, 2)}%"
        if total_casos > 0 else "N/A"
    )

    if tab == "tab-overview":

        fig_pizza = px.pie(
            names=["Vacinados (≥1 dose)", "Não vacinados"],
            values=[vacinados, nao_vacinados],
            title=f"Cobertura Vacinal — {pais}",
            template="plotly_dark"
        )

        fig_barras = px.bar(
            x=["Casos Totais", "Mortes Totais"],
            y=[total_casos, total_mortes],
            title=f"Casos x Mortes — {pais}",
            labels={"x": "Indicador", "y": "Quantidade"},
            template="plotly_dark"
        )

        fig_pizza.update_layout(height=450)
        fig_barras.update_layout(height=450)

        return html.Div([

            html.Div([
                html.Div(f"Casos Totais: {total_casos:,}".replace(",", "."), className="card"),
                html.Div(f"Mortes Totais: {total_mortes:,}".replace(",", "."), className="card"),
                html.Div(f"Letalidade: {letalidade}", className="card"),
                html.Div(f"Vacinados (≥1 dose): {vacinados:,}".replace(",", "."), className="card"),
                html.Div(f"Esquema completo: {completamente_vacinados:,}".replace(",", "."), className="card"),
            ], className="card-container"),

            html.Div([
                dcc.Graph(figure=fig_pizza),
                dcc.Graph(figure=fig_barras)
            ], className="graficos-container")

        ])

    if tab == "tab-casos":

        if dff["casos_mm7"].isna().all():
            return html.Div("Sem dados suficientes para casos.", style={"padding": "30px"})

        fig = px.line(
            dff,
            x="date",
            y="casos_mm7",
            title=f"Casos (Média móvel 7 dias) — {pais}",
            template="plotly_dark"
        )
        fig.update_layout(height=500)

        return dcc.Graph(figure=fig)

    if tab == "tab-obitos":

        if dff["mortes_mm7"].isna().all():
            return html.Div("Sem dados suficientes para óbitos.", style={"padding": "30px"})

        fig = px.line(
            dff,
            x="date",
            y="mortes_mm7",
            title=f"Óbitos (Média móvel 7 dias) — {pais}",
            template="plotly_dark"
        )
        fig.update_layout(height=500)

        return dcc.Graph(figure=fig)

    if tab == "tab-vacinacao":

        if vacinados == 0 and completamente_vacinados == 0:
            return html.Div("Sem dados de vacinação.", style={"padding": "30px"})

        fig = px.line(
            dff,
            x="date",
            y=["people_vaccinated", "people_fully_vaccinated"],
            labels={"value": "Pessoas", "variable": "Tipo", "date": "Data"},
            title=f"Progresso da Vacinação — {pais}",
            template="plotly_dark"
        )
        fig.update_layout(height=500)

        return dcc.Graph(figure=fig)