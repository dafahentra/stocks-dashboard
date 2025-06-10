import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from curl_cffi import requests

# Currency mapping and symbols
CURRENCY_MAP = {
    '.DE': 'EUR', '.F': 'EUR', '.L': 'GBP', '.PA': 'EUR', '.AS': 'EUR',
    '.MI': 'EUR', '.MC': 'EUR', '.T': 'JPY', '.HK': 'HKD', '.SS': 'CNY',
    '.SZ': 'CNY', '.BO': 'INR', '.NS': 'INR', '.AX': 'AUD', '.KS': 'KRW',
    '.TW': 'TWD', '.SI': 'SGD', '.JK': 'IDR', '.BK': 'THB', '.TO': 'CAD',
    '.SA': 'BRL', '.MX': 'MXN', '.SW': 'CHF'
}

CURRENCY_SYMBOLS = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥',
    'INR': '₹', 'AUD': 'A$', 'CAD': 'C$', 'CHF': '₣', 'HKD': 'HK$',
    'SGD': 'S$', 'KRW': '₩', 'TWD': 'NT$', 'IDR': 'Rp', 'THB': '฿',
    'BRL': 'R$', 'MXN': 'MX$'
}

@st.cache_resource
def get_session():
    """Get curl_cffi session for yfinance"""
    return requests.Session(impersonate="chrome")

def get_currency(ticker):
    """Get currency for ticker"""
    try:
        session = get_session()
        info = yf.Ticker(ticker, session=session).info
        if 'currency' in info:
            return info['currency']
    except:
        pass
    
    # Fallback to suffix mapping
    for suffix, currency in CURRENCY_MAP.items():
        if ticker.upper().endswith(suffix):
            return currency
    return 'USD'

def format_price(price, currency):
    """Format price with currency symbol"""
    symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')
    if currency in ['JPY', 'KRW', 'IDR']:
        return f"{symbol}{price:,.0f}"
    return f"{symbol}{price:,.2f}"

@st.cache_data(ttl=30)
def fetch_data(ticker, period, interval):
    """Fetch stock data with caching"""
    try:
        session = get_session()
        yf_ticker = yf.Ticker(ticker, session=session)
        
        if period == '1wk':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            data = yf_ticker.history(start=start_date, end=end_date, interval=interval)
        else:
            data = yf_ticker.history(period=period, interval=interval)
        
        if data.empty:
            return pd.DataFrame()
        
        # Process timezone
        if data.index.tzinfo is None:
            data.index = data.index.tz_localize('UTC')
        data.index = data.index.tz_convert('US/Eastern')
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
        
        return data
    except Exception as e:
        st.error(f"Error fetching {ticker}: {str(e)}")
        return pd.DataFrame()

def add_indicators(data):
    """Add technical indicators"""
    if data.empty or len(data) < 20:
        return data
    
    # Moving averages
    data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
    data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    
    # RSI
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()
    data['MACD_Hist'] = macd.macd_diff()
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(data['Close'])
    data['BB_Upper'] = bb.bollinger_hband()
    data['BB_Lower'] = bb.bollinger_lband()
    data['BB_Middle'] = bb.bollinger_mavg()
    
    return data

def calculate_metrics(data):
    """Calculate basic metrics"""
    if data.empty:
        return None, None, None, None, None, None
    
    last_close = data['Close'].iloc[-1]
    first_close = data['Close'].iloc[0]
    change = last_close - first_close
    pct_change = (change / first_close) * 100 if first_close != 0 else 0
    high = data['High'].max()
    low = data['Low'].min()
    volume = data['Volume'].sum()
    
    return last_close, change, pct_change, high, low, volume

def create_price_chart(data, ticker, currency, chart_type, indicators):
    """Create main price chart"""
    fig = go.Figure()
    
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=data['Datetime'],
            open=data['Open'], 
            high=data['High'],
            low=data['Low'], 
            close=data['Close'],
            name=ticker,
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data['Datetime'], 
            y=data['Close'],
            mode='lines', 
            name=f'{ticker} Close',
            line=dict(width=3, color='#6366f1')
        ))
    
    # Add indicators
    colors = ['#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ef4444']
    color_idx = 0
    
    for indicator in indicators:
        if indicator == 'SMA 20' and 'SMA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['SMA_20'],
                name='SMA 20', line=dict(color=colors[color_idx % len(colors)], width=2)
            ))
            color_idx += 1
            
        elif indicator == 'SMA 50' and 'SMA_50' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['SMA_50'],
                name='SMA 50', line=dict(color=colors[color_idx % len(colors)], width=2)
            ))
            color_idx += 1
            
        elif indicator == 'EMA 20' and 'EMA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['EMA_20'],
                name='EMA 20', line=dict(color=colors[color_idx % len(colors)], width=2)
            ))
            color_idx += 1
            
        elif indicator == 'Bollinger Bands' and 'BB_Upper' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['BB_Upper'],
                name='BB Upper', line=dict(color='#94a3b8', width=1),
                opacity=0.7
            ))
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['BB_Lower'],
                name='BB Lower', line=dict(color='#94a3b8', width=1),
                fill='tonexty', fillcolor='rgba(99, 102, 241, 0.2)',
                opacity=0.7
            ))
            fig.add_trace(go.Scatter(
                x=data['Datetime'], y=data['BB_Middle'],
                name='BB Middle', line=dict(color='#94a3b8', width=2)
            ))
    
    fig.update_layout(
        title=f"{ticker} - {currency}",
        xaxis_title="Time", 
        yaxis_title=f"Price ({currency})",
        height=650,
        hovermode='x unified'
    )
    
    return fig

def create_volume_chart(data):
    """Create volume chart"""
    vol_colors = ['#10b981' if c >= o else '#ef4444' 
                  for c, o in zip(data['Close'], data['Open'])]
    
    fig = go.Figure(data=go.Bar(
        x=data['Datetime'], y=data['Volume'],
        marker_color=vol_colors, opacity=0.7, name='Volume'
    ))
    
    fig.update_layout(
        title="Trading Volume",
        height=250,
        showlegend=False
    )
    
    return fig

def create_rsi_chart(data):
    """Create RSI chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Datetime'], y=data['RSI'],
        name='RSI', line=dict(color='#6366f1', width=3)
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981")
    
    fig.update_layout(
        title="RSI (14)", 
        height=300,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_macd_chart(data):
    """Create MACD chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Datetime'], y=data['MACD'],
        name='MACD', line=dict(color='#3b82f6')
    ))
    fig.add_trace(go.Scatter(
        x=data['Datetime'], y=data['MACD_Signal'],
        name='Signal', line=dict(color='#ef4444')
    ))
    
    if 'MACD_Hist' in data.columns:
        colors_macd = ['#10b981' if x >= 0 else '#ef4444' for x in data['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=data['Datetime'], y=data['MACD_Hist'],
            name='Histogram', marker_color=colors_macd, opacity=0.6
        ))
    
    fig.update_layout(
        title="MACD", 
        height=300
    )
    
    return fig

def styled_metric(text, color_bg, color_text):
    """Create styled metric display"""
    st.markdown(
        f"""
        <div style="
            background-color: {color_bg};
            padding: 10px 15px;
            border-radius: 6px;
            color: {color_text};
            font-weight: 600;
            font-size: 1.05em;
            margin-bottom: 8px;
        ">
            {text}
        </div>
        """, unsafe_allow_html=True
    )