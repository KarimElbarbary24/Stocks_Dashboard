import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from stocks import Stocks
import plotly.express as px

# Initialize the Stocks class and database connection
stocks = Stocks()

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

# Fetch available stock symbols (replace this with a more dynamic list if needed)
dropdown_options = [
    {"label": "Apple (AAPL)", "value": "AAPL"},
    {"label": "Google (GOOGL)", "value": "GOOGL"},
]

# Layout
app.layout = html.Div([
    html.H1("Stock Dashboard", style={"text-align": "center", "margin-bottom": "20px"}),

    html.Div([
        html.Label("Select a stock:", style={"font-weight": "bold"}),
        dcc.Dropdown(
            id="stock-dropdown",
            options=dropdown_options,
            value="AAPL",
            style={"width": "50%"}
        ),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.RadioItems(
            id="indicator-toggle",
            options=[
                {"label": "Show Technical Indicators", "value": "show"},
                {"label": "Hide Technical Indicators", "value": "hide"}
            ],
            value="show",
            inline=True,
            style={"margin-bottom": "20px"}
        )
    ]),

    html.Div(id="stock-graph-container", children=[]),
    html.Div(id="fundamental-data-container", children=[], style={"margin-top": "40px"}),

    html.Div([
        html.P("Data provided by Alpha Vantage", style={"text-align": "center", "font-style": "italic", "color": "gray"}),
    ], style={"margin-top": "50px"})
])

# Callbacks
@app.callback(
    [Output("stock-graph-container", "children"),
     Output("fundamental-data-container", "children")],
    [Input("stock-dropdown", "value"),
     Input("indicator-toggle", "value")]
)
def update_graph_and_fundamental_data(stock_symbol, indicator_toggle):
    try:
        # Ensure data exists in the database
        query = f"SELECT COUNT(*) FROM stock_data WHERE symbol = '{stock_symbol}'"
        with stocks.engine.connect() as conn:
            result = conn.execute(query).scalar()

        if result == 0:
            print(f"No data for {stock_symbol}. Fetching...")
            df = stocks.fetch_stock_data(stock_symbol)
            stocks.upload_stock_data(df)
        else:
            df = stocks.get_stock_data(stock_symbol)

        # Add technical indicators
        if indicator_toggle == "show":
            stocks.calculate_technical_indicators(stock_symbol)
            df = stocks.get_stock_data(stock_symbol)

        # Plot the data
        fig = px.line(
            df,
            x="date",
            y=["close"] + (["ma_50", "bollinger_upper", "bollinger_lower"] if indicator_toggle == "show" else []),
            labels={"value": "Price", "date": "Date"},
            title=f"{stock_symbol} Stock Prices" + (" with Technical Indicators" if indicator_toggle == "show" else "")
        )

        # Fetch fundamental data
        stocks.fetch_and_upload_fundamental_data(stock_symbol)

        # Retrieve fundamental data
        query = f"""
        SELECT report_date, revenue, earnings, pe_ratio, dividend_yield
        FROM fundamental_data
        WHERE symbol = '{stock_symbol}'
        ORDER BY report_date DESC
        LIMIT 1;
        """
        fundamental_data = pd.read_sql_query(query, con=stocks.engine)

        if not fundamental_data.empty:
            fundamental_data_html = html.Div([
                html.H3("Fundamental Data", style={"text-align": "center", "margin-bottom": "20px"}),
                html.Table([
                    html.Tr([html.Th("Metric"), html.Th("Value")], style={"background-color": "#f8f9fa"}),
                    html.Tr([html.Td("Report Date"), html.Td(fundamental_data.iloc[0]['report_date'])]),
                    html.Tr([html.Td("Revenue"), html.Td(fundamental_data.iloc[0]['revenue'])]),
                    html.Tr([html.Td("Earnings"), html.Td(fundamental_data.iloc[0]['earnings'])]),
                    html.Tr([html.Td("P/E Ratio"), html.Td(fundamental_data.iloc[0]['pe_ratio'])]),
                    html.Tr([html.Td("Dividend Yield"), html.Td(fundamental_data.iloc[0]['dividend_yield'])]),
                ], style={"width": "50%", "margin": "auto", "border-collapse": "collapse", "border": "1px solid black"})
            ])
        else:
            fundamental_data_html = html.Div([
                html.H3("Fundamental Data", style={"text-align": "center"}),
                html.P("No fundamental data available.")
            ])

        return dcc.Graph(figure=fig), fundamental_data_html

    except Exception as e:
        error_message = html.Div([
            html.H3("Error: Could not retrieve or process stock data."),
            html.P(str(e))
        ])
        return error_message, error_message

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
