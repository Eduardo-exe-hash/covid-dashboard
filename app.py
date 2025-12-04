import dash
from dash import Dash, html, dcc

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)
server = app.server

app.title = "COVID-19 | Análise Interativa"

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        dcc.Link("🏠 Início", href="/", className="nav-link"),
        dcc.Link("📊 Dashboard", href="/dashboard", className="nav-link"),
    ], className="navbar"),

    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
