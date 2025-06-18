
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# --- Dados ---
df = pd.read_excel("dados.xlsx", sheet_name="pedidos")
df_metas = pd.read_excel("dados.xlsx", sheet_name="metas")
df_metas.columns = ["Indústria", "Meta Valor Anual", "Meta Positivação Anual"]

df["Data"] = pd.to_datetime(df["Data da Venda"])
df["Ano"] = df["Data"].dt.year
df["Mês"] = df["Data"].dt.strftime('%b')
df["Mês_Num"] = df["Data"].dt.month

# Logo local
logo_path = "logo_mikeias.jpeg"
with open(logo_path, "rb") as f:
    encoded_logo = base64.b64encode(f.read()).decode()

# --- App Layout ---

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

server = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "mikeiasrepresentacoes": generate_password_hash("37951672")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@server.before_request
@auth.login_required
def before_request():
    pass


app = dash.Dash(__name__, server=server, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.title = "Dashboard com Abas e Donuts por Indústria"


app.layout = html.Div([
    html.Button("☰ Filtros", id="toggle-filtros", n_clicks=0, style={
        "position": "fixed",
        "top": "10px",
        "left": "10px",
        "zIndex": "999",
        "backgroundColor": "#2980b9",
        "color": "white",
        "border": "none",
        "padding": "10px 15px",
        "borderRadius": "5px",
        "fontSize": "16px",
        "display": "block"
    }),

    html.Div(id="painel-filtros", children=[html.Div([
        html.Img(src="data:image/jpeg;base64," + encoded_logo,
                 style={"width": "100%", "margin-bottom": "20px"}),
        html.H2("Painel de Filtros", style={"color": "white", "text-align": "center", "margin-bottom": "20px"}),
        html.Label("Cidade", style={"color": "white"}),
        dcc.Dropdown(id="filtro-cidade", multi=True, placeholder="Cidade"),
        html.Label("Cliente", style={"color": "white", "margin-top": "10px"}),
        dcc.Dropdown(id="filtro-cliente", multi=True, placeholder="Cliente"),
        html.Label("Indústria", style={"color": "white", "margin-top": "10px"}),
        dcc.Dropdown(id="filtro-industria", multi=True, placeholder="Indústria"),
        html.Label("Ano", style={"color": "white", "margin-top": "10px"}),
        dcc.Dropdown(id="filtro-ano", multi=True, placeholder="Ano"),
        html.Label("Mês", style={"color": "white", "margin-top": "10px"}),
        dcc.Dropdown(id="filtro-mes", multi=True, placeholder="Mês"),
        html.Button("Limpar Filtros", id="btn-reset", n_clicks=0, style={
            "margin-top": "20px", "width": "100%", "backgroundColor": "#2980b9", "color": "white", "border": "none", "padding": "10px"
        }),
        html.Label("Centro dos Donuts", style={"color": "white", "margin-top": "20px"}),
        dcc.RadioItems(
            id="tipo-centro-donut",
            options=[
                {"label": "Percentual (%)", "value": "percent"},
                {"label": "Valor (R$)", "value": "valor"}
            ],
            value="percent",
            inline=True,
            style={"color": "white"}
        )
    ], style={
        "flex": "1", "minWidth": "180px", "maxWidth": "220px", "width": "100%",
"minWidth": "160px",
"padding": "20px",
"background-color": "#1f2c56",
"height": "100vh",
"position": "sticky",
"top": "0px",
"overflowY": "auto",
"fontFamily": "Segoe UI, Roboto, sans-serif",
        "background-color": "#1f2c56",
        "height": "100vh",
        "position": "sticky",
        "top": "0px",
        "overflowY": "auto",
        "fontFamily": "Segoe UI, Roboto, sans-serif"
    })], style={"display": "block"}),

    html.Div([
        html.Div(id="cards", style={
            "display": "flex",
            "gap": "20px",
            "margin-bottom": "20px",
            "position": "sticky",
            "top": "0px",
            "zIndex": 10,
            "backgroundColor": "#f4f6f8",
            "padding": "10px 0",
            "flexWrap": "wrap",
            "fontFamily": "Segoe UI, Roboto, sans-serif"
        }),

        html.Div(
            dcc.Tabs(id="aba-principal", value="visao", children=[
                dcc.Tab(label="📊 Visão Geral", value="visao"),
                dcc.Tab(label="🏙️ Cidades", value="cidade"),
                dcc.Tab(label="👥 Clientes", value="cliente"),
                dcc.Tab(label="📦 Produtos", value="produto"),
            ]),
            style={
                "position": "sticky",
                "top": "80px",
                "zIndex": 9,
                "backgroundColor": "#f4f6f8",
                "fontFamily": "Segoe UI, Roboto, sans-serif"
            }
        ),

        html.Div(id="conteudo-abas"),
        html.Div(id="detalhamento", style={"margin-top": "30px"})
    ], style={
        "flex": "3",
"minWidth": "0",
"padding": "20px",
"overflowY": "scroll",
"height": "100vh",
"backgroundColor": "#f4f6f8",
"fontFamily": "Segoe UI, Roboto, sans-serif",
        "overflowY": "scroll",
        "height": "100vh",
        "backgroundColor": "#f4f6f8",
        "fontFamily": "Segoe UI, Roboto, sans-serif"
    })
], style={"display": "flex", "flexWrap": "wrap", "flexDirection": "row", "margin": "0", "padding": "0", "fontFamily": "Segoe UI, Roboto, sans-serif"})




@app.callback(
    Output("painel-filtros", "style"),
    Input("toggle-filtros", "n_clicks"),
    Input("filtro-cidade", "value"),
    Input("filtro-cliente", "value"),
    Input("filtro-industria", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("aba-principal", "value"),
    State("painel-filtros", "style"),
    prevent_initial_call=True
)
def toggle_filtros(n_clicks, cidade, cliente, industria, ano, mes, aba, current_style):
    ctx = dash.callback_context
    if not ctx.triggered or not current_style:
        return current_style

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "toggle-filtros":
        # Toggle manual
        if current_style.get("display") == "none":
            current_style["display"] = "block"
        else:
            current_style["display"] = "none"
    else:
        # Fechar ao interagir com filtros ou aba
        current_style["display"] = "none"

    return current_style
