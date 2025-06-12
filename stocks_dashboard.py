import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from curl_cffi import requests

# Import components and styles
from components import (
    get_session, get_currency, format_price, fetch_data, 
    add_indicators, calculate_metrics, create_price_chart,
    create_volume_chart, create_rsi_chart, create_macd_chart,
    styled_metric, CURRENCY_MAP, CURRENCY_SYMBOLS # Import CURRENCY_MAP, CURRENCY_SYMBOLS
)
from styles import apply_dark_theme, create_header, COLORS # Removed get_metric_style

# Configure page
st.set_page_config(
    page_title="Stock Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# Apply dark theme
apply_dark_theme() #

# Create elegant header
create_header() #

# Sidebar controls
with st.sidebar:
    st.markdown("### Dashboard Settings")
    
    ticker = st.text_input("Stock Ticker", "GOTO.JK", help="e.g., AAPL, GOOGL, BMW.DE").upper()
    
    period = st.selectbox("Time Period", 
                         ['1d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y'], 
                         index=2)
    
    chart_type = st.selectbox("Chart Type", ['Candlestick', 'Line'])
    
    st.markdown("### Technical Indicators")
    indicators = st.multiselect("Select Indicators",
                               ['SMA 20', 'SMA 50', 'EMA 20', 'Bollinger Bands', 'RSI', 'MACD'],
                               default=['SMA 20', 'EMA 20'])
    
    st.markdown("### Display Options")
    show_volume = st.checkbox("Show Volume", True)
    auto_refresh = st.checkbox("Auto Refresh", False)
    
    if auto_refresh:
        st.rerun()

# Interval mapping
intervals = {
    '1d': '5m', '1wk': '30m', '1mo': '1d', '3mo': '1d',
    '6mo': '1wk', '1y': '1wk', '2y': '1wk', '5y': '1mo'
}

# Main dashboard
if st.sidebar.button("Update Dashboard", type="primary") or auto_refresh:
    with st.spinner(f"Loading {ticker} data..."):
        data = fetch_data(ticker, period, intervals[period])
        
        if not data.empty:
            data = add_indicators(data)
            currency = get_currency(ticker)
            last_close, change, pct_change, high, low, volume = calculate_metrics(data)
            
            if last_close is not None:
                # Display key metrics with enhanced styling
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", 
                              format_price(last_close, currency), 
                              f"{format_price(change, currency)} ({pct_change:.2f}%)",
                              delta_color="normal") #
                
                with col2:
                    st.metric("Daily High", format_price(high, currency)) #
                
                with col3:
                    st.metric("Daily Low", format_price(low, currency)) #
                
                with col4:
                    st.metric("Volume", f"{volume:,}") #
                
                # Tabs
                tab1, tab2, tab3 = st.tabs(["Price Chart", "Technical Analysis", "Data Summary"]) #
                
                with tab1:
                    # Main chart
                    fig = create_price_chart(data, ticker, currency, chart_type, indicators)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume chart
                    if show_volume and not data['Volume'].isna().all():
                        fig_vol = create_volume_chart(data)
                        st.plotly_chart(fig_vol, use_container_width=True)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    # RSI
                    if 'RSI' in indicators and 'RSI' in data.columns:
                        with col1:
                            fig_rsi = create_rsi_chart(data)
                            st.plotly_chart(fig_rsi, use_container_width=True)
                    
                    # MACD
                    if 'MACD' in indicators and 'MACD' in data.columns:
                        with col2:
                            fig_macd = create_macd_chart(data)
                            st.plotly_chart(fig_macd, use_container_width=True)
                
                with tab3:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Recent Price Data")
                        price_df = data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].tail(15)
                        st.dataframe(price_df, use_container_width=True)

                    with col2:
                        st.subheader("Analysis Summary")

                        # Price trend
                        if pct_change > 0:
                            styled_metric(f"Bullish: +{pct_change:.2f}%", COLORS['success'], COLORS['text_primary']) #
                        else:
                            styled_metric(f"Bearish: {pct_change:.2f}%", COLORS['danger'], COLORS['text_primary']) #

                        # RSI analysis
                        if 'RSI' in data.columns and not data['RSI'].isna().iloc[-1]:
                            rsi_val = data['RSI'].iloc[-1]
                            if rsi_val > 70:
                                styled_metric(f"RSI: {rsi_val:.1f} (Overbought)", COLORS['warning'], COLORS['text_primary']) #
                            elif rsi_val < 30:
                                styled_metric(f"RSI: {rsi_val:.1f} (Oversold)", COLORS['info'], COLORS['text_primary']) #
                            else:
                                styled_metric(f"RSI: {rsi_val:.1f} (Neutral)", COLORS['bg_tertiary'], COLORS['text_secondary']) #

                        # MA signals
                        if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
                            sma20 = data['SMA_20'].iloc[-1]
                            sma50 = data['SMA_50'].iloc[-1]
                            if sma20 > sma50:
                                styled_metric("MA Signal: Bullish", COLORS['success'], COLORS['text_primary']) #
                            else:
                                styled_metric("MA Signal: Bearish", COLORS['danger'], COLORS['text_primary']) #

                        # Volume analysis
                        avg_vol = data['Volume'].mean()
                        curr_vol = data['Volume'].iloc[-1]
                        if curr_vol > avg_vol * 1.5:
                            styled_metric("Volume: High", COLORS['info'], COLORS['text_primary']) #
                        elif curr_vol < avg_vol * 0.5:
                            styled_metric("Volume: Low", COLORS['warning'], COLORS['text_primary']) #
                        else:
                            styled_metric("Volume: Normal", COLORS['bg_tertiary'], COLORS['text_secondary']) #
            
        else:
            st.error(f"Unable to fetch data for {ticker}")

# Watchlist sidebar
with st.sidebar:
    st.header("Quick Watchlist")
    
    watchlist = {
        'US Tech': ['AAPL', 'GOOGL', 'MSFT', 'AMZN'],
        'European': ['SAP.DE', 'ASML.AS', 'NESN.SW'],
        'Asian': ['TSM', '7203.T', 'BABA'],
        'Emerging': ['BBCA.JK', 'VALE', 'INFY']
    }
    
    for category, symbols in watchlist.items():
        with st.expander(category):
            for symbol in symbols:
                try:
                    quick_data = fetch_data(symbol, '1d', '5m')
                    if not quick_data.empty:
                        curr_price = quick_data['Close'].iloc[-1]
                        open_price = quick_data['Open'].iloc[0]
                        change = curr_price - open_price
                        pct = (change / open_price) * 100 if open_price != 0 else 0
                        
                        st.metric(symbol, f"{curr_price:.2f}", f"{change:.2f} ({pct:.2f}%)", delta_color="normal") #
                except:
                    st.metric(symbol, "N/A", "Error") #

    st.markdown("---")
    st.caption("Data: Yahoo Finance | © Dafa Hentra 2025")