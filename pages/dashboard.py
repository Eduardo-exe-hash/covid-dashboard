import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from dados_loader import carregar_dados_covid

dash.register_page(
    __name__,
    path="/dashboard",
    name="Dashboard"
)

df = carregar_dados_covid()
paises = df["location"].unique()

layout = html.Div([

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
        value="tab-overview",
        children=[
            dcc.Tab(label="Visão Geral", value="tab-overview"),
            dcc.Tab(label="Casos", value="tab-casos"),
            dcc.Tab(label="Óbitos", value="tab-obitos"),
            dcc.Tab(label="Vacinação", value="tab-vacinacao"),
            dcc.Tab(label="Gráficos", value="tab-graficos"),   # <---- NOVA ABA
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

    dff["new_cases"] = dff["new_cases"].clip(lower=0)
    dff["new_deaths"] = dff["new_deaths"].clip(lower=0)

    dff["casos_mm7"] = dff["new_cases"].rolling(7).mean()
    dff["mortes_mm7"] = dff["new_deaths"].rolling(7).mean()

    dff["people_vaccinated"] = dff["people_vaccinated"].fillna(0)
    dff["people_fully_vaccinated"] = dff["people_fully_vaccinated"].fillna(0)
    dff["total_vaccinations"] = dff["total_vaccinations"].fillna(0)

    ultimo = dff.iloc[-1]

    vacinados = int(ultimo["people_vaccinated"])
    completamente_vacinados = int(ultimo["people_fully_vaccinated"])

    total_casos = int(ultimo["total_cases"]) if pd.notna(ultimo["total_cases"]) else 0
    total_mortes = int(ultimo["total_deaths"]) if pd.notna(ultimo["total_deaths"]) else 0

   
    if tab == "tab-overview":
        letalidade = f"{round((total_mortes / total_casos) * 100, 2)}%" if total_casos > 0 else "N/A"

        # Grafico de Pizza (Vacinados x Não vacinados)
        fig_pizza = px.pie(
            names=["Vacinados", "Não totalmente vacinados"],
            values=[vacinados, total_casos - vacinados if total_casos > 0 else 0],
            title=f"Distribuição da Vacinação — {pais}",
            template="plotly_dark"
        )

        # Grafico de Barras(Casos x Mortes)
        fig_barras = px.bar(
            x=["Casos Totais", "Mortes Totais"],
            y=[total_casos, total_mortes],
            title=f"Casos x Mortes — {pais}",
            labels={"x": "Indicador", "y": "Quantidade"},
            template="plotly_dark"
        )

        fig_barras.update_layout(height=450)
        fig_pizza.update_layout(height=450)

        return html.Div([
            html.Div([
                html.Div(f"Casos Totais: {total_casos:,}".replace(",", "."), className="card"),
                html.Div(f"Mortes Totais: {total_mortes:,}".replace(",", "."), className="card"),
                html.Div(f"Letalidade: {letalidade}", className="card"),
                html.Div(f"Vacinados (≥1 dose): {vacinados:,}".replace(",", "."), className="card"),
                html.Div(f"Esquema completo: {completamente_vacinados:,}".replace(",", "."), className="card")
            ], className="card-container"),

            # Gráficos adicionados
            html.Div([
                dcc.Graph(figure=fig_pizza),
                dcc.Graph(figure=fig_barras)
            ], className="graficos-container")
        ])

    #  ABA CASOS
    if tab == "tab-casos":
        if dff["casos_mm7"].isna().all():
            return html.Div("Sem dados de casos suficientes para plotar.", style={"padding": "20px"})
        fig_casos = px.line(
            dff, x="date", y="casos_mm7",
            template="plotly_dark",
            title=f"Casos (média móvel 7 dias) — {pais}"
        )
        fig_casos.update_layout(height=500)
        return html.Div([dcc.Graph(figure=fig_casos)])

    #  ABA ÓBITOS
    if tab == "tab-obitos":
        if dff["mortes_mm7"].isna().all():
            return html.Div("Sem dados de óbitos suficientes para plotar.", style={"padding": "20px"})
        fig_obitos = px.line(
            dff, x="date", y="mortes_mm7",
            template="plotly_dark",
            title=f"Óbitos (média móvel 7 dias) — {pais}"
        )
        fig_obitos.update_layout(height=500)
        return html.Div([dcc.Graph(figure=fig_obitos)])

    # ABA VACINAÇÃO
    
    if tab == "tab-vacinacao":
        fig_vac = px.line(
            dff,
            x="date",
            y=["people_vaccinated", "people_fully_vaccinated"],
            labels={"value": "Pessoas", "date": "Data", "variable": "Tipo"},
            title=f"Progresso da Vacinação — {pais}",
            template="plotly_dark"
        )
        fig_vac.update_layout(height=500)
        return dcc.Graph(figure=fig_vac)

    
    #   ABA GRÁFICOS 
    if tab == "tab-graficos":

        fig_pizza = px.pie(
            names=["Vacinados", "Completamente vacinados"],
            values=[vacinados, completamente_vacinados],
            title=f"Proporção de Vacinação — {pais}",
            template="plotly_dark"
        )

        fig_barras2 = px.bar(
            x=["Casos Totais", "Mortes Totais"],
            y=[total_casos, total_mortes],
            title=f"Casos Totais x Mortes Totais — {pais}",
            labels={"x": "Indicador", "y": "Quantidade"},
            template="plotly_dark"
        )

        fig_pizza.update_layout(height=450)
        fig_barras2.update_layout(height=450)

        return html.Div([
            dcc.Graph(figure=fig_pizza),
            dcc.Graph(figure=fig_barras2)
        ], className="graficos-container")
