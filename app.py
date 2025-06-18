
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
    html.Div([
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
        "flex": "1", "minWidth": "250px",
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
    }),

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
    Output("filtro-cidade", "options"),
    Output("filtro-cliente", "options"),
    Output("filtro-industria", "options"),
    Output("filtro-ano", "options"),
    Output("filtro-mes", "options"),
    Input("btn-reset", "n_clicks")
)
def atualizar_opcoes(n):
    return (
        [{"label": c, "value": c} for c in sorted(df["Cidade"].unique())],
        [{"label": c, "value": c} for c in sorted(df["Cliente"].unique())],
        [{"label": c, "value": c} for c in sorted(df["Indústria"].unique())],
        [{"label": str(a), "value": a} for a in sorted(df["Ano"].unique())],
        [{"label": m, "value": m} for m in df["Mês"].unique()]
    )

@app.callback(
    Output("filtro-cidade", "value"),
    Output("filtro-cliente", "value"),
    Output("filtro-industria", "value"),
    Output("filtro-ano", "value"),
    Output("filtro-mes", "value"),
    Input("btn-reset", "n_clicks")
)
def limpar_filtros(n):
    return None, None, None, None, None

@app.callback(
    Output("cards", "children"),
    Input("filtro-cidade", "value"),
    Input("filtro-cliente", "value"),
    Input("filtro-industria", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value")
)
def atualizar_cards(cidades, clientes, industrias, anos, meses):
    dff = df.copy()
    if cidades: dff = dff[dff["Cidade"].isin(cidades)]
    if clientes: dff = dff[dff["Cliente"].isin(clientes)]
    if industrias: dff = dff[dff["Indústria"].isin(industrias)]
    if anos: dff = dff[dff["Ano"].isin(anos)]
    if meses: dff = dff[dff["Mês"].isin(meses)]

    total = dff["Valor da Venda (R$)"].sum()
    pedidos = len(dff)
    clientes_ativos = dff["Cliente"].nunique()
    industrias_ativas = dff["Indústria"].nunique()

    return [
        html.Div([html.H4("💰 Vendas"), html.H3(f"R$ {total:,.2f}")], style={"padding": "15px", "backgroundColor": "#ffffff", "borderRadius": "10px", "boxShadow": "0 2px 6px rgba(0,0,0,0.1)", "flex": "1", "minWidth": "140px", "maxWidth": "220px", "textAlign": "center"}),
        html.Div([html.H4("📦 Pedidos"), html.H3(pedidos)], style={"padding": "15px", "backgroundColor": "#ffffff", "borderRadius": "10px", "boxShadow": "0 2px 6px rgba(0,0,0,0.1)", "flex": "1", "minWidth": "140px", "maxWidth": "220px", "textAlign": "center"}),
        html.Div([html.H4("👥 Clientes"), html.H3(clientes_ativos)], style={"padding": "15px", "backgroundColor": "#ffffff", "borderRadius": "10px", "boxShadow": "0 2px 6px rgba(0,0,0,0.1)", "flex": "1", "minWidth": "140px", "maxWidth": "220px", "textAlign": "center"}),
        html.Div([html.H4("🏭 Indústrias"), html.H3(industrias_ativas)], style={"padding": "15px", "backgroundColor": "#ffffff", "borderRadius": "10px", "boxShadow": "0 2px 6px rgba(0,0,0,0.1)", "flex": "1", "minWidth": "140px", "maxWidth": "220px", "textAlign": "center"})
    ]

@app.callback(
    Output("conteudo-abas", "children"),
    Input("aba-principal", "value"),
    Input("filtro-cidade", "value"),
    Input("filtro-cliente", "value"),
    Input("filtro-industria", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("tipo-centro-donut", "value")
)
def atualizar_aba(aba, cidades, clientes, industrias, anos, meses, tipo_centro):
    dff = df.copy()
    if cidades: dff = dff[dff["Cidade"].isin(cidades)]
    if clientes: dff = dff[dff["Cliente"].isin(clientes)]
    if industrias: dff = dff[dff["Indústria"].isin(industrias)]
    if anos: dff = dff[dff["Ano"].isin(anos)]
    if meses: dff = dff[dff["Mês"].isin(meses)]

    if aba == "visao":
        resumo = dff.groupby("Indústria")["Valor da Venda (R$)"].sum().reset_index()
        resumo = resumo.merge(df_metas, on="Indústria", how="left")
        resumo["% Meta"] = (resumo["Valor da Venda (R$)"] / resumo["Meta Valor Anual"]).fillna(0)

        
        donuts = []
        for _, row in resumo.iterrows():
            valor = row["Valor da Venda (R$)"]
            meta = row["Meta Valor Anual"]
            restante = max(meta - valor, 0)
            porcentagem = row["% Meta"]
            cor_donut = "#2ecc71" if porcentagem >= 1 else "#e74c3c"
            texto = f"{int(min(porcentagem, 1)*100)}%" if tipo_centro == "percent" else f"R${valor/1e3:.0f} mil"

            fig = go.Figure(data=[
                go.Pie(
                    values=[valor, restante],
                    labels=["Realizado", "Restante"],
                    hole=0.7,
                    marker_colors=[cor_donut, "#e0e0e0"],
                    textinfo="none"
                )
            ])
            fig.update_layout(
                annotations=[
                    dict(text=texto, x=0.5, y=0.5, font_size=18, showarrow=False),
                    dict(text=row["Indústria"], x=0.5, y=0.15, font_size=12, showarrow=False)
                ],
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                height=200,
                width=200
            )
            donuts.append(dcc.Graph(figure=fig, style={"width": "100%", "maxWidth": "240px", "margin": "10px"}))

        return html.Div([
            html.Div(donuts, style={"display": "flex", "flex-wrap": "wrap", "justify-content": "center"})
        ])


    elif aba == "cliente":
        ranking = dff.groupby("Cliente")["Valor da Venda (R$)"].sum().reset_index()
        ranking = ranking.sort_values(by="Valor da Venda (R$)", ascending=False).reset_index(drop=True)
        ranking["Posição"] = ranking.index + 1

        tabela = dash_table.DataTable(
            columns=[
                {"name": "Posição", "id": "Posição"},
                {"name": "Cliente", "id": "Cliente"},
                {"name": "Valor da Venda (R$)", "id": "Valor da Venda (R$)", "type": "numeric", "format": {"specifier": ".2f"}}
            ],
            data=ranking.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px", "fontFamily": "Segoe UI"},
            style_header={"backgroundColor": "#2980b9", "color": "white", "fontWeight": "bold"},
            style_data={"backgroundColor": "#ffffff"},
            style_table={"overflowX": "auto"},
            page_size=15
        )
        return html.Div([html.H4("Ranking de Clientes"), tabela])


    elif aba == "produto":
        if "Produto" in dff.columns:
            fig = px.pie(dff.groupby("Produto")["Valor da Venda (R$)"].sum().nlargest(10).reset_index(),
                         names="Produto", values="Valor da Venda (R$)", title="Participação por Produto")
        else:
            fig = go.Figure()
        return dcc.Graph(figure=fig)

    elif aba == "cidade":
        ranking = dff.groupby("Cidade")["Valor da Venda (R$)"].sum().reset_index()
        ranking = ranking.sort_values(by="Valor da Venda (R$)", ascending=False).reset_index(drop=True)
        ranking["Posição"] = ranking.index + 1

        tabela = dash_table.DataTable(
            columns=[
                {"name": "Posição", "id": "Posição"},
                {"name": "Cidade", "id": "Cidade"},
                {"name": "Valor da Venda (R$)", "id": "Valor da Venda (R$)", "type": "numeric", "format": {"specifier": ".2f"}}
            ],
            data=ranking.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px", "fontFamily": "Segoe UI"},
            style_header={"backgroundColor": "#2980b9", "color": "white", "fontWeight": "bold"},
            style_data={"backgroundColor": "#ffffff"},
            style_table={"overflowX": "auto"},
            page_size=15
        )
        return html.Div([html.H4("Ranking de Cidades"), tabela])

    elif aba == "cliente":
        ranking = dff.groupby("Cliente")["Valor da Venda (R$)"].sum().reset_index()
        ranking = ranking.sort_values(by="Valor da Venda (R$)", ascending=False).reset_index(drop=True)
        ranking["Posição"] = ranking.index + 1

        tabela = dash_table.DataTable(
            columns=[
                {"name": "Posição", "id": "Posição"},
                {"name": "Cliente", "id": "Cliente"},
                {"name": "Valor da Venda (R$)", "id": "Valor da Venda (R$)", "type": "numeric", "format": {"specifier": ".2f"}}
            ],
            data=ranking.to_dict("records"),
            style_cell={"textAlign": "left", "padding": "5px", "fontFamily": "Segoe UI"},
            style_header={"backgroundColor": "#2980b9", "color": "white", "fontWeight": "bold"},
            style_data={"backgroundColor": "#ffffff"},
            style_table={"overflowX": "auto"},
            page_size=15
        )
        return html.Div([html.H4("Ranking de Clientes"), tabela])

    return html.Div("Nenhum gráfico disponível.")

if __name__ == "__main__":
    app.run(debug=True)


# Expor o objeto app como server para o Gunicorn
app = app.server
