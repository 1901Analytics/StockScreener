import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import datetime
import plotly.express as px


# url or file of the ticker source
sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
djia_url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'


st.title('A Basic Stock Screener Demonstration in Streamlit')

# Sidebar
with st.form(key = 'StockQuery', clear_on_submit = False):
    with st.sidebar:
        st.sidebar.subheader('Query parameters')
        stock_universe = st.sidebar.selectbox('Are you interested in the S&P 500 or the Dow Jones Industrial Average?',
                                      ['', 'S&P500', 'DJIA'])
        start_date = st.sidebar.date_input("Start date", datetime.date(2019, 1, 1))
        end_date = st.sidebar.date_input("End date", datetime.date.today())

        # Retrieving tickers data
        if stock_universe:
            if stock_universe == 'S&P500':
                ticker_list = pd.read_html(sp500_url, flavor = 'html5lib')[0]['Symbol']
            if stock_universe == 'DJIA':
                ticker_list = pd.read_html(djia_url, flavor='html5lib')[1]['Symbol']

            tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol
            tickerData = yf.Ticker(tickerSymbol) # Get ticker data
            tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker
            tickerDf.dropna(inplace=True)


        query_submit = st.form_submit_button(label='Submit Stock Query')

if query_submit:
    # Ticker information
    st.image(tickerData.info['logo_url'])

    string_name = tickerData.info['longName']
    st.header('**%s**' % string_name)

    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)

    # Ticker data
    st.subheader('Ticker data for ' + str(string_name))
    st.write(tickerDf)

    st.subheader('Price over time for ' + str(string_name))
    fig1 = px.scatter(tickerDf, x=tickerDf.index, y='Close', trendline="ols")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader('CAPM plot for ' + str(string_name) + ' over the period ' + str(start_date) + ' through ' + str(end_date))
    spy_data = pd.DataFrame(yf.download('SPY', start=start_date, end=end_date)['Adj Close']).rename(columns = {'Adj Close': 'SPY Price'})
    spy_data['SPY Rets'] = spy_data['SPY Price'].pct_change()
    tickerDf['Stock Rets'] = tickerDf['Close'].pct_change()
    CAPM_data = spy_data.join(tickerDf).dropna()
    beta, intercept = np.polyfit(CAPM_data['SPY Rets'], CAPM_data['Stock Rets'], 1)
    st.markdown('**Beta**: {:.4f}%'.format(beta))
    st.markdown('**Intercept**: {:.4f}%'.format(intercept))

    fig2 = px.scatter(CAPM_data, x='SPY Rets', y='Stock Rets', trendline="ols")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader('The 10 most recent analyst recommendations for ' + str(string_name))
    recos = tickerData.get_recommendations().drop(columns = ['From Grade', 'Action'])
    recos.dropna(inplace = True)
    st.dataframe(recos.tail(10))










