import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from curl_cffi import requests
from styles import COLORS

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
    """Create main price chart without gaps"""
    fig = go.Figure()
    
    # Filter data to remove non-trading periods
    filtered_data = data[
        (data['Volume'] > 0) & 
        (data['High'] > 0) & 
        (data['Low'] > 0) &
        (data['Close'] > 0) &
        (data['Open'] > 0)
    ].copy()
    
    if filtered_data.empty:
        filtered_data = data.copy()
    
    # Reset index for continuous x-axis
    filtered_data.reset_index(drop=True, inplace=True)
    x_positions = list(range(len(filtered_data)))
    
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=x_positions,
            open=filtered_data['Open'], 
            high=filtered_data['High'],
            low=filtered_data['Low'], 
            close=filtered_data['Close'],
            name=ticker,
            increasing_line_color=COLORS['success'],
            decreasing_line_color=COLORS['danger']
        ))
    else:
        fig.add_trace(go.Scatter(
            x=x_positions, 
            y=filtered_data['Close'],
            mode='lines', 
            name=f'{ticker} Close',
            line=dict(width=2, color=COLORS['primary'])
        ))
    
    # Add indicators
    colors = [COLORS['secondary'], COLORS['warning'], COLORS['info'], COLORS['primary'], COLORS['danger']]
    color_idx = 0
    
    for indicator in indicators:
        if indicator == 'SMA 20' and 'SMA_20' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['SMA_20'],
                name='SMA 20', line=dict(color=colors[color_idx % len(colors)], width=1.5)
            ))
            color_idx += 1
            
        elif indicator == 'SMA 50' and 'SMA_50' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['SMA_50'],
                name='SMA 50', line=dict(color=colors[color_idx % len(colors)], width=1.5)
            ))
            color_idx += 1
            
        elif indicator == 'EMA 20' and 'EMA_20' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['EMA_20'],
                name='EMA 20', line=dict(color=colors[color_idx % len(colors)], width=1.5)
            ))
            color_idx += 1
            
        elif indicator == 'Bollinger Bands' and 'BB_Upper' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Upper'],
                name='BB Upper', line=dict(color=COLORS['text_muted'], width=1),
                opacity=0.5
            ))
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Lower'],
                name='BB Lower', line=dict(color=COLORS['text_muted'], width=1),
                fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)',
                opacity=0.5
            ))
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Middle'],
                name='BB Middle', line=dict(color=COLORS['text_muted'], width=1.5, dash='dash')
            ))
    
    # Create custom tick labels
    n_ticks = min(10, len(filtered_data))
    tick_interval = max(1, len(filtered_data) // n_ticks)
    tickvals = list(range(0, len(filtered_data), tick_interval))
    ticktext = []
    
    for i in tickvals:
        if i < len(filtered_data):
            dt = filtered_data['Datetime'].iloc[i]
            if len(filtered_data) <= 50:
                ticktext.append(dt.strftime('%m/%d %H:%M'))
            else:
                ticktext.append(dt.strftime('%m/%d/%y'))
    
    fig.update_layout(
        title=f"{ticker} - {currency}",
        xaxis_title="Time", 
        yaxis_title=f"Price ({currency})",
        height=600,
        hovermode='x unified',
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_secondary'],
        font=dict(color=COLORS['text_primary'])
    )
    
    return fig

def create_volume_chart(data):
    """Create volume chart"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    vol_colors = [COLORS['success'] if c >= o else COLORS['danger']
                    for c, o in zip(data_copy['Close'], data_copy['Open'])]
    
    fig = go.Figure(data=go.Bar(
        x=data_copy['x_index'], 
        y=data_copy['Volume'],
        marker_color=vol_colors, 
        opacity=0.7
    ))
    
    # Configure x-axis
    n_points = len(data_copy)
    step = max(1, n_points // 10)
    tick_indices = list(range(0, n_points, step))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d') for i in tick_indices]
    
    fig.update_layout(
        title="Trading Volume",
        height=200,
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_secondary'],
        font=dict(color=COLORS['text_primary'])
    )
    
    return fig

def create_rsi_chart(data):
    """Create RSI chart"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['RSI'],
        name='RSI', line=dict(color=COLORS['primary'], width=2)
    ))
    fig.add_hline(y=70, line_dash="dash", line_color=COLORS['danger'])
    fig.add_hline(y=30, line_dash="dash", line_color=COLORS['success'])
    
    # Configure x-axis
    n_points = len(data_copy)
    step = max(1, n_points // 10)
    tick_indices = list(range(0, n_points, step))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d') for i in tick_indices]
    
    fig.update_layout(
        title="RSI (14)",
        height=250,
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor=COLORS['border']),
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_secondary'],
        font=dict(color=COLORS['text_primary'])
    )
    
    return fig

def create_macd_chart(data):
    """Create MACD chart"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['MACD'],
        name='MACD', line=dict(color=COLORS['info'])
    ))
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['MACD_Signal'],
        name='Signal', line=dict(color=COLORS['danger'])
    ))
    
    if 'MACD_Hist' in data_copy.columns:
        colors_macd = [COLORS['success'] if x >= 0 else COLORS['danger'] for x in data_copy['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=data_copy['x_index'], y=data_copy['MACD_Hist'],
            name='Histogram', marker_color=colors_macd, opacity=0.6
        ))
    
    # Configure x-axis
    n_points = len(data_copy)
    step = max(1, n_points // 10)
    tick_indices = list(range(0, n_points, step))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d') for i in tick_indices]
    
    fig.update_layout(
        title="MACD",
        height=250,
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['border']
        ),
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_secondary'],
        font=dict(color=COLORS['text_primary'])
    )
    
    return fig

def styled_metric(text, color_bg, color_text):
    """Create styled metric display"""
    st.markdown(
        f"""
        <div style="
            background-color: {color_bg};
            padding: 8px 12px;
            border-radius: 4px;
            color: {color_text};
            font-weight: 500;
            margin-bottom: 5px;
        ">
            {text}
        </div>
        """, unsafe_allow_html=True
    )