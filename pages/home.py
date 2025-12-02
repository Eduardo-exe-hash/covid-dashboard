import dash
from dash import html

dash.register_page(
    __name__,
    path="/",
    name="Home"
)

layout = html.Div([
    html.H1("A Pandemia de COVID-19", className="titulo"),

    html.P(
        "Este projeto apresenta uma análise interativa da pandemia de COVID-19 "
        "utilizando dados públicos do Our World in Data.",
        className="texto"
    ),

    html.H3("O que você vai encontrar"),
    html.Ul([
        html.Li("Evolução dos casos ao longo do tempo"),
        html.Li("Evolução dos óbitos"),
        html.Li("Indicadores agregados por região ou país"),
    ]),

    html.P(
        "Utilize o botão abaixo para acessar o dashboard interativo.",
        className="texto"
    ),

    html.A(
        "Ir para o Dashboard",
        href="/dashboard",
        className="btn"
    )
], className="container")
