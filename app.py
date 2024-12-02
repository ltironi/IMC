import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import os
import datetime
import csv

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Portfolio Insights"
server = app.server

PORTFOLIO_FILE = 'data/portfolio.csv'
BENCHMARK_FILE = 'data/benchmarks.csv'

# Sample portfolio data
try:
    portfolio = pd.read_csv(PORTFOLIO_FILE)
except FileNotFoundError:
    portfolio = pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-01", "2024-01-01"],
        "Ticker": ["AAPL", "MSFT", "GOOG"],
        "Weight": [40, 35, 25]
    })
    portfolio.to_csv(PORTFOLIO_FILE, index=False)

# Sample benchmark data
try:
    benchmarks = pd.read_csv(BENCHMARK_FILE)
except FileNotFoundError:
    benchmarks = pd.DataFrame({
        "Name": ["100% SPY", "100% World", "60% Equity / 40% Bonds"],
        "Tickers": ["SPY", "VT", "SPY,IEF"],
        "Weights": ["1", "1", "0.6,0.4"]
    })
    benchmarks.to_csv(BENCHMARK_FILE, index=False)

# Layout
app.layout = html.Div(
    className="container",
    children=[
        # Existing row: Current Allocation and Performance
        html.Div(
            id="row-panels",
            className="row",
            children=[
                # Left Panel
                html.Div(
                    id="left-pan",
                    className="panel left",
                    children=[
                        html.H5("Current Asset Allocation"),
                        dcc.Graph(id="current-allocation-pie"),
                        html.H5("Portfolio KPIs"),
                        html.Div(id="portfolio-kpis"),
                        html.H5("Performance of Individual Assets"),
                        dcc.Graph(id="assets-performance-chart"),
                    ],
                ),
                # Center Panel
                html.Div(
                    id="center-pan",
                    className="panel center",
                    children=[
                        html.H5("Portfolio Performance"),
                        dcc.Graph(id="portfolio-performance"),
                        html.Div(
                            className="dropdown-container",
                            children=[
                                html.Label("Select Timeframe:"),
                                dcc.Dropdown(
                                    id="timeframe-dropdown",
                                    options=[
                                        {"label": "1 Month", "value": "1mo"},
                                        {"label": "3 Months", "value": "3mo"},
                                        {"label": "6 Months", "value": "6mo"},
                                        {"label": "1 Year", "value": "1y"}
                                    ],
                                    value="6mo",
                                    clearable=False
                                ),
                                html.Label("Select Benchmark:"),
                                dcc.Dropdown(
                                    id="benchmark-dropdown",
                                    options=[
                                        {"label": "100% SPY", "value": "100% SPY"},
                                        {"label": "100% World", "value": "100% World"},
                                        {"label": "60% Equity / 40% Bonds", "value": "60% Equity / 40% Bonds"}
                                    ],
                                    value="100% SPY",
                                    clearable=False
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # New row: Search ticker and visualize price action
        html.Div(
            id="row-ticker-search",
            className="row full-width",
            children=[
                html.Div(
                    id="search-panel",
                    className="panel full-width",
                    children=[
                        html.H5("Search Ticker and Visualize Price Action"),
                        html.Div(
                            className="search-container",
                            children=[
                                dcc.Input(
                                    id="ticker-input",
                                    type="text",
                                    placeholder="Enter Ticker Symbol (e.g., AAPL)",
                                    style={"width": "40%", "margin-right": "10px"}
                                ),
                                html.Button(
                                    "Search",
                                    id="search-button",
                                    n_clicks=0,
                                    style={
                                        "padding": "10px 20px",
                                        "background-color": "#499BF8",
                                        "color": "white",
                                        "border": "none",
                                        "border-radius": "5px"
                                    }
                                ),
                            ],
                        ),
                        dcc.Graph(id="ticker-price-chart"),  # Candlestick chart for the ticker
                    ],
                ),
            ],
        ),
        html.Div(
            id="row-portfolio-allocation",
            className="row full-width",
            children=[
                html.Div(
                    id="allocation-panel",
                    className="panel full-width",
                    children=[
                        html.H5("Update Portfolio Allocation"),
                        html.Button(
                            "Add Asset",
                            id="add-asset-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 20px",
                                "background-color": "#499BF8",
                                "color": "white",
                                "border": "none",
                                "border-radius": "5px",
                                "margin-bottom": "20px"
                            }
                        ),
                        html.Div(
                            id="allocation-table",
                            children=[
                                # Placeholder for dynamically created rows
                            ]
                        ),
                        html.Button(
                            "Save Allocation",
                            id="save-allocation-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 20px",
                                "background-color": "#E8C547",
                                "color": "black",
                                "border": "none",
                                "border-radius": "5px",
                                "margin-top": "20px"
                            }
                        ),
                        html.Div(
                            id="save-allocation-message",
                            className="message",
                            style={"margin-top": "10px", "color": "red"}
                        ),
                    ],
                ),
            ],
        ),
    ]
)


# Callback
@app.callback(
    Output('current-allocation-pie', 'figure'),
    Output('portfolio-performance', 'figure'),
    Output('portfolio-kpis', 'children'),
    Output('assets-performance-chart', 'figure'),
    Input('timeframe-dropdown', 'value'),
    Input('benchmark-dropdown', 'value')
)
def update_panels(timeframe, selected_benchmark):
    # Read portfolio data
    print("Portfolio File Path:", PORTFOLIO_FILE)
    portfolio = pd.read_csv(PORTFOLIO_FILE)

    # Create pie chart for allocation
    pie_chart = go.Figure(
        data=[go.Pie(labels=portfolio["Ticker"], values=portfolio["Weight"])]
    )
    pie_chart.update_traces(hole=0.8, textinfo='percent+label')
    pie_chart.update_layout(
        title=dict(
            text="Current Asset Allocation",
            x=0.5,
            font=dict(size=18, color='#9fa6b7')
        ),
        margin=dict(t=50, b=20, l=20, r=20),
        height=300,
        paper_bgcolor='#262A3A',
        font=dict(color='#9fa6b7')
    )

    # Fetch portfolio price data
    tickers = portfolio["Ticker"].tolist()
    weights = pd.Series(portfolio["Weight"].values, index=portfolio["Ticker"]) / 100
    price_data = yf.download(tickers, period=timeframe, interval="1d")["Adj Close"]

    # Calculate portfolio performance
    portfolio_returns = price_data.pct_change().mul(weights, axis=1).sum(axis=1)
    portfolio_cum_returns = (1 + portfolio_returns).cumprod()

    # Fetch benchmark data
    benchmark_row = benchmarks.loc[benchmarks["Name"] == selected_benchmark].iloc[0]
    benchmark_tickers = benchmark_row["Tickers"].split(",")
    benchmark_weights = pd.Series(
        list(map(float, benchmark_row["Weights"].split(","))),
        index=benchmark_tickers
    )
    benchmark_price_data = yf.download(benchmark_tickers, period=timeframe, interval="1d")["Adj Close"]
    benchmark_returns = benchmark_price_data.pct_change().mul(benchmark_weights, axis=1).sum(axis=1)
    benchmark_cum_returns = (1 + benchmark_returns).cumprod()

    # Create performance chart
    performance_chart = go.Figure()
    performance_chart.add_trace(go.Scatter(
        x=portfolio_cum_returns.index,
        y=portfolio_cum_returns.values,
        mode='lines',
        name='Portfolio',
        line=dict(color='#E8C547', width=2)
    ))
    performance_chart.add_trace(go.Scatter(
        x=benchmark_cum_returns.index,
        y=benchmark_cum_returns.values,
        mode='lines',
        name=selected_benchmark,
        line=dict(color='#499BF8', width=2)
    ))
    performance_chart.update_layout(
        title=f"Portfolio vs {selected_benchmark} Over {timeframe}",
        xaxis_title="Date",
        yaxis_title="Cumulative Returns",
        paper_bgcolor='#262A3A',
        plot_bgcolor='#262A3A',
        font=dict(color='#9fa6b7'),
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",  # Align to the bottom of the legend box
            y=1.02,  # Position above the chart
            xanchor="center",  # Center horizontally
            x=0.5  # Align to the center of the chart
        )
    )


    # Performance of Individual Assets
    assets_chart = go.Figure()
    for ticker in tickers:
        asset_cum_returns = (1 + price_data[ticker].pct_change()).cumprod()
        assets_chart.add_trace(go.Scatter(
            x=asset_cum_returns.index,
            y=asset_cum_returns.values,
            mode='lines',
            name=ticker
        ))
    assets_chart.update_layout(
        title=dict(
            text="Performance of Individual Assets",
            x=0.5,  # Center the title
            font=dict(size=14, color='#9fa6b7'),
            pad=dict(t=10)  # Add padding above the title
        ),
        xaxis_title="Date",
        yaxis_title="Cumulative Returns",
        paper_bgcolor='#262A3A',
        plot_bgcolor='#262A3A',
        font=dict(color='#9fa6b7'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=300,  # Limit chart height
        margin=dict(t=40, b=20, l=20, r=20)  # Adjust margins for better spacing
    )



    # Portfolio KPIs
    total_return = portfolio_cum_returns.iloc[-1] - 1
    rolling_max = portfolio_cum_returns.cummax()
    max_drawdown = ((portfolio_cum_returns / rolling_max) - 1).min()
    kpis = [
        html.P(f"Total Return: {total_return:.2%}"),
        html.P(f"Max Drawdown: {max_drawdown:.2%}")
    ]

    return pie_chart, performance_chart, kpis, assets_chart


@app.callback(
    Output('ticker-price-chart', 'figure'),
    Input('search-button', 'n_clicks'),
    State('ticker-input', 'value')
)
def update_ticker_chart(n_clicks, ticker):
    if not ticker:
        # Return a placeholder chart if no ticker is entered
        return go.Figure().update_layout(
            title="Enter a Ticker to View Price Action",
            xaxis_title="Date",
            yaxis_title="Price",
            paper_bgcolor='#262A3A',
            plot_bgcolor='#262A3A',
            font=dict(color='#9fa6b7'),
            height=600  # Slightly increased height for the placeholder
        )

    try:
        # Fetch 2 years of price data for the specified ticker
        data = yf.download(ticker.upper(), period="2y", interval="1d")

        # Check if data is a multi-index and select the specific ticker if necessary
        if isinstance(data.columns, pd.MultiIndex):
            open_prices = data['Open'][ticker.upper()]
            high_prices = data['High'][ticker.upper()]
            low_prices = data['Low'][ticker.upper()]
            close_prices = data['Close'][ticker.upper()]
        else:
            open_prices = data['Open']
            high_prices = data['High']
            low_prices = data['Low']
            close_prices = data['Close']

        # Check if data is retrieved and contains valid entries
        if close_prices.empty:
            raise ValueError(f"No valid price data found for ticker: {ticker.upper()}")

        # Calculate moving averages
        ma_9 = close_prices.rolling(window=9).mean()
        ma_50 = close_prices.rolling(window=50).mean()
        ma_200 = close_prices.rolling(window=200).mean()

        # Create a candlestick chart
        fig = go.Figure(data=[
            go.Candlestick(
                x=close_prices.index,
                open=open_prices.values,
                high=high_prices.values,
                low=low_prices.values,
                close=close_prices.values,
                name=f"{ticker.upper()} Candlestick",
                increasing=dict(line=dict(color='#499BF8')),  # Highlight color for increasing candles
                decreasing=dict(line=dict(color='#9B1D20'))   # Carmin color for decreasing candles
            ),
            go.Scatter(
                x=ma_9.index,
                y=ma_9.values,
                mode='lines',
                name="9-Day MA",
                line=dict(color='#E8C547', width=1.5)  # Saffron color for the 9-day moving average
            ),
            go.Scatter(
                x=ma_50.index,
                y=ma_50.values,
                mode='lines',
                name="50-Day MA",
                line=dict(color='#69E2B8', width=1.5)  # Aqua color for the 50-day moving average
            ),
            go.Scatter(
                x=ma_200.index,
                y=ma_200.values,
                mode='lines',
                name="200-Day MA",
                line=dict(color='#9fa6b7', width=1.5)  # Font color for the 200-day moving average
            )
        ])
        fig.update_layout(
            title=f"{ticker.upper()} Price Action with Moving Averages (Last 2 Years)",
            xaxis_title="Date",
            yaxis_title="Price",
            paper_bgcolor='#262A3A',
            plot_bgcolor='#262A3A',
            font=dict(color='#9fa6b7'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            height=700  # Slightly increased height for better visibility
        )
        return fig

    except Exception as e:
        # Handle errors gracefully
        print(f"Error: {e}")  # Debugging: Print the error
        return go.Figure().update_layout(
            title=f"Error: Unable to Fetch Data for {ticker.upper()}",
            xaxis_title="Date",
            yaxis_title="Price",
            paper_bgcolor='#262A3A',
            plot_bgcolor='#262A3A',
            font=dict(color='#9fa6b7'),
            height=600  # Placeholder chart height
        )



@app.callback(
    Output('allocation-table', 'children'),
    Input('add-asset-button', 'n_clicks'),
    State('allocation-table', 'children'),
    prevent_initial_call=False
)
def manage_allocation_table(n_clicks, current_rows):
    # Load current allocation from the portfolio file when the app starts
    if current_rows is None or n_clicks == 0:
        if os.path.exists(PORTFOLIO_FILE):
            try:
                # Read the portfolio file
                portfolio = pd.read_csv(PORTFOLIO_FILE)
                current_allocation = portfolio[["Ticker", "Weight"]].to_dict("records")
            except Exception as e:
                print(f"Error reading {PORTFOLIO_FILE}: {e}")
                current_allocation = []  # Fallback to empty allocation
        else:
            current_allocation = []  # Fallback if file doesn't exist

        # Create input rows based on current allocation
        rows = [
            html.Div(
                className="allocation-row",
                children=[
                    dcc.Input(
                        type="text",
                        value=allocation["Ticker"],
                        placeholder="Ticker",
                        style={"width": "45%", "margin-right": "10px"},
                        className="ticker-input"
                    ),
                    dcc.Input(
                        type="number",
                        value=allocation["Weight"],
                        placeholder="Weight (%)",
                        style={"width": "45%"},
                        className="weight-input"
                    )
                ]
            )
            for allocation in current_allocation
        ]
        return rows

    # Add a new empty row when "Add Asset" is clicked
    new_row = html.Div(
        className="allocation-row",
        children=[
            dcc.Input(
                type="text",
                placeholder="Ticker",
                style={"width": "45%", "margin-right": "10px"},
                className="ticker-input"
            ),
            dcc.Input(
                type="number",
                placeholder="Weight (%)",
                style={"width": "45%"},
                className="weight-input"
            )
        ]
    )
    current_rows.append(new_row)
    return current_rows


@app.callback(
    Output('save-allocation-message', 'children'),  # Update the message div
    Input('save-allocation-button', 'n_clicks'),
    State('allocation-table', 'children')
)
def save_allocation(n_clicks, rows):
    if n_clicks > 0:
        allocation = []

        # Collect allocation data from inputs
        for row in rows:
            inputs = row['props']['children']
            ticker = inputs[0]['props'].get('value', "").strip()  # Get ticker and strip spaces
            weight = inputs[1]['props'].get('value', None)  # Get weight as numeric or None
            if ticker and weight is not None:  # Only include valid rows
                allocation.append({"ticker": ticker, "weight": float(weight)})

        # Validate the total weight
        total_weight = sum(entry["weight"] for entry in allocation)
        if abs(total_weight - 100) > 1e-6:  # Allow for floating-point precision issues
            print(f"Error: Total weight is {total_weight}, which is not 100.")
            return f"Error: Total weight is {total_weight:.2f}%. Ensure weights sum to 100%."

        # Write the new allocation to the CSV file (replacing the file)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)

            with open(PORTFOLIO_FILE, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Ticker", "Weight"])  # Write header
                for entry in allocation:
                    writer.writerow([today, entry["ticker"], entry["weight"]])  # Write rows

            print(f"Portfolio saved to {PORTFOLIO_FILE}: {allocation}")
            return "Portfolio Saved Successfully!"
        except Exception as e:
            print(f"Error saving allocation: {e}")
            return "Error saving allocation. Please check the file."

    return ""



if __name__ == '__main__':
    app.run_server(debug=True)