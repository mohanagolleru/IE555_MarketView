import streamlit as st
import requests
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import ta


# Alpha Vantage API key
API_KEY = "76FY8EGY1TS5IX50"

# Define function to get stock data and company overview
def get_stock_data(symbol, exchange):
    # Get daily stock price data
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={API_KEY}"
    if exchange:
        url += f"&market={exchange}"
    response = requests.get(url)
    data = response.json()["Time Series (Daily)"]
    X = pd.DataFrame.from_dict(data, orient="index")
    X.index = pd.to_datetime(X.index)
    X = X.astype(float)
    X = X.drop(columns=["7. dividend amount","8. split coefficient"])
    df = X.rename(columns={'1. open':'Open','2. high':'High','3. low':'Low','4. close':'Close','5. adjusted close':'Adj Close','6. volume': 'Volume'})
    df = df.sort_index(ascending=True) # Sort dataframe by date in ascending order
    

    # Get company overview data
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    company_name = data.get('Name')
    industry = data.get('Industry')
    ebitda = data.get('EBITDA')
    pe_ratio = data.get('PERatio')
    pb_ratio = data.get('PriceToBookRatio')
    book_value = data.get('BookValue')
    ev_to_revenue = data.get('EVToRevenue')
    ev_to_ebitda = data.get('EVToEBITDA')
    beta = data.get('Beta')
    eps = data.get('EPS')
    peg_ratio = data.get('PEGRatio')
    forward_pe = data.get('ForwardPE')
    analyst_target_price = data.get('AnalystTargetPrice')
    high_52_weeks = data.get('52WeekHigh')
    low_52_weeks = data.get('52WeekLow')
    
    company_overview_data = {'Name':[company_name],'Industry': [industry],'Analyst Target Price': [analyst_target_price],
                             'Book Value': [book_value],'P/B Ratio': [pb_ratio], 'P/E Ratio': [pe_ratio], 
                             'Forward P/E': [forward_pe], 'EV/Revenue': [ev_to_revenue], 
                             'EV/EBITDA': [ev_to_ebitda], 'Beta': [beta], '52 Week High': [high_52_weeks], 
                             '52 Week Low': [low_52_weeks],'EPS': [eps], 'PEG Ratio': [peg_ratio]}
    # Display the company overview data as a table
    st.write('Company Overview')
    st.dataframe(pd.DataFrame.from_dict(company_overview_data).iloc[:20, :20])


    return df

# Define the Streamlit app
def main():
    st.set_page_config(page_title="Market View", page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="collapsed")
    st.title(":chart_with_upwards_trend: Market View")

    # Ask user to input stock symbol
    symbol = st.sidebar.text_input("Enter stock symbol (e.g. AAPL, MSFT, IBM):", key="symbol_input")
    if not symbol:
        st.warning("Please enter a stock symbol in the search bar present towards the left to continue")
        return

    # Call the get_stock_data function
    df = get_stock_data(symbol, 'NASDAQ')

    # Calculate the MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    # Calculate the RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

    # Add checkboxes for MACD and RSI
    show_macd = st.sidebar.checkbox("Show MACD", value=True)
    show_rsi = st.sidebar.checkbox("Show RSI", value=True)

    # Create the stock price chart using mplfinance
    fig_stock, ax_stock = mpf.plot(df, type='candle', mav=(35, 50), volume=True, tight_layout=True,
                                   style='nightclouds', figratio=(20, 12), figscale=0.95,
                                   returnfig=True, mavcolors=('yellow', 'red'))
    # Display the stock price chart
    ax_stock[0].set_title("Security Performance", fontsize=18)  # Increase the title fontsize
    st.pyplot(fig_stock)


    # Create the MACD plot if checkbox is selected
    if show_macd:
        fig_macd, ax_macd = plt.subplots(figsize=(12, 4))
        ax_macd.plot(macd, color='yellow', linewidth=2, label='MACD')
        ax_macd.plot(signal, color='red', linewidth=2, label='Signal')
        ax_macd.axhline(0, color='gray', linestyle='--')
        ax_macd.legend()
        ax_macd.set_title("MACD", fontsize=24)  # Increase the title fontsize
        st.pyplot(fig_macd)

    # Create the RSI plot if checkbox is selected
    if show_rsi:
        fig_rsi, ax_rsi = plt.subplots(figsize=(12, 4))
        ax_rsi.plot(df['RSI'], color='blue', linewidth=2, label='RSI')
        ax_rsi.axhline(30, color='red', linestyle='--', alpha=1)
        ax_rsi.axhline(70, color='red', linestyle='--', alpha=1)
        ax_rsi.legend()
        ax_rsi.set_title("RSI", fontsize=24)  # Increase the title fontsize
        st.pyplot(fig_rsi)

if __name__ == '__main__':
    main()





