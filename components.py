import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from curl_cffi import requests
from styles import COLORS, CHART_COLORS # Import CHART_COLORS from styles.py

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
    """Create main price chart without gaps (TradingView style)"""
    fig = go.Figure()
    
    # Filter data to remove rows with zero volume or invalid prices
    # This helps eliminate non-trading periods
    filtered_data = data[
        (data['Volume'] > 0) & 
        (data['High'] > 0) & 
        (data['Low'] > 0) &
        (data['Close'] > 0) &
        (data['Open'] > 0)
    ].copy()
    
    # If no data after filtering, use original data
    if filtered_data.empty:
        filtered_data = data.copy()
    
    # Reset index to create continuous x-axis
    filtered_data.reset_index(drop=True, inplace=True)
    
    # Create custom x-axis labels using index positions
    x_positions = list(range(len(filtered_data)))
    
    if chart_type == 'Candlestick':
        # Create custom hover text for candlestick
        hover_text = []
        for i, row in filtered_data.iterrows():
            hover_text.append(
                f"Time: {row['Datetime'].strftime('%Y-%m-%d %H:%M:%S')}<br>" +
                f"Open: {row['Open']:.2f}<br>" +
                f"High: {row['High']:.2f}<br>" +
                f"Low: {row['Low']:.2f}<br>" +
                f"Close: {row['Close']:.2f}"
            )
        
        fig.add_trace(go.Candlestick(
            x=x_positions,  # Use index positions instead of datetime
            open=filtered_data['Open'], 
            high=filtered_data['High'],
            low=filtered_data['Low'], 
            close=filtered_data['Close'],
            name=ticker,
            increasing_line_color=COLORS['success'], # Use COLORS
            decreasing_line_color=COLORS['danger'], # Use COLORS
            xaxis='x',
            yaxis='y',
            hovertext=hover_text,
            hoverinfo='text'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=x_positions, 
            y=filtered_data['Close'],
            mode='lines', 
            name=f'{ticker} Close',
            line=dict(width=3, color=COLORS['primary']), # Use COLORS
            hovertemplate='Time: %{customdata}<br>' +
                         'Price: %{y:.2f}<extra></extra>',
            customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    # Add indicators with clean hover
    colors = CHART_COLORS['indicators'] # Use CHART_COLORS['indicators']
    if not colors: # Fallback if not defined
        colors = [COLORS['chart_primary'], COLORS['chart_secondary'], COLORS['chart_tertiary'], COLORS['chart_quaternary'], COLORS['chart_quinary']]

    color_idx = 0
    
    for indicator in indicators:
        if indicator == 'SMA 20' and 'SMA_20' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['SMA_20'],
                name='SMA 20', line=dict(color=colors[color_idx % len(colors)], width=2),
                hovertemplate='Time: %{customdata}<br>Value: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            color_idx += 1
            
        elif indicator == 'SMA 50' and 'SMA_50' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['SMA_50'],
                name='SMA 50', line=dict(color=colors[color_idx % len(colors)], width=2),
                hovertemplate='Time: %{customdata}<br>Value: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            color_idx += 1
            
        elif indicator == 'EMA 20' and 'EMA_20' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['EMA_20'],
                name='EMA 20', line=dict(color=colors[color_idx % len(colors)], width=2),
                hovertemplate='Time: %{customdata}<br>Value: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            color_idx += 1
            
        elif indicator == 'Bollinger Bands' and 'BB_Upper' in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Upper'],
                name='BB Upper', line=dict(color=COLORS['text_muted'], width=1), # Use COLORS
                opacity=0.7,
                hovertemplate='Time: %{customdata}<br>BB Upper: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Lower'],
                name='BB Lower', line=dict(color=COLORS['text_muted'], width=1), # Use COLORS
                fill='tonexty', fillcolor=COLORS['bollinger'], # Use COLORS
                opacity=0.7,
                hovertemplate='Time: %{customdata}<br>BB Lower: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
            fig.add_trace(go.Scatter(
                x=x_positions, y=filtered_data['BB_Middle'],
                name='BB Middle', line=dict(color=COLORS['text_muted'], width=2), # Use COLORS
                hovertemplate='Time: %{customdata}<br>BB Middle: %{y:.2f}<extra></extra>',
                customdata=filtered_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    # Create custom tick labels for x-axis
    # Show every nth label to avoid overcrowding
    n_ticks = min(10, len(filtered_data))  # Maximum 10 ticks
    tick_interval = max(1, len(filtered_data) // n_ticks)
    
    tickvals = list(range(0, len(filtered_data), tick_interval))
    ticktext = []
    
    for i in tickvals:
        if i < len(filtered_data):
            dt = filtered_data['Datetime'].iloc[i]
            if hasattr(dt, 'strftime'):
                # Format datetime based on time period
                if len(filtered_data) <= 50:  # Short period - show time
                    ticktext.append(dt.strftime('%m/%d %H:%M'))
                else:  # Long period - show date only
                    ticktext.append(dt.strftime('%m/%d/%y'))
            else:
                ticktext.append(str(dt))
    
    fig.update_layout(
        title=f"{ticker} - {currency}",
        xaxis_title="Time", 
        yaxis_title=f"Price ({currency})",
        height=650,
        hovermode='x unified',
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=True,
            gridcolor=COLORS['border'], # Use COLORS
            rangeslider=dict(visible=False),  # Hide rangeslider for cleaner look
            showticklabels=True,  # Show custom labels
            ticks="",  # Hide tick marks
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['border'], # Use COLORS
        ),
        # Remove gaps between candlesticks
        bargap=0,
        bargroupgap=0,
        # Clean hover appearance
        hoverlabel=dict(
            bgcolor=COLORS['bg_primary'], # Use COLORS
            bordercolor=COLORS['border'], # Use COLORS
            font_size=12,
        )
    )
    
    return fig

def create_volume_chart(data):
    """Create volume chart without gaps"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    vol_colors = [COLORS['success'] if c >= o else COLORS['danger'] # Use COLORS
                  for c, o in zip(data_copy['Close'], data_copy['Open'])]
    
    fig = go.Figure(data=go.Bar(
        x=data_copy['x_index'], 
        y=data_copy['Volume'],
        marker_color=vol_colors, 
        opacity=0.7, 
        name='Volume',
        hovertemplate='<b>Volume</b><br>' +
                     'Date: %{customdata}<br>' +
                     'Volume: %{y:,}<br>' +
                     '<extra></extra>',
        customdata=data_copy['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
    ))
    
    # Configure x-axis similar to price chart
    n_points = len(data_copy)
    if n_points > 20:
        step = max(1, n_points // 10)
        tick_indices = list(range(0, n_points, step))
        if tick_indices[-1] != n_points - 1:
            tick_indices.append(n_points - 1)
    else:
        tick_indices = list(range(n_points))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d %H:%M') if 'hour' in str(data_copy.iloc[i]['Datetime'])
                  else data_copy.iloc[i]['Datetime'].strftime('%m/%d') 
                  for i in tick_indices]
    
    fig.update_layout(
        title="Trading Volume",
        height=250,
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            type='linear',
            showgrid=True,
            gridcolor=COLORS['bg_tertiary'] # Use COLORS
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['bg_tertiary'] # Use COLORS
        )
    )
    
    return fig

def create_rsi_chart(data):
    """Create RSI chart without gaps"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['RSI'],
        name='RSI', line=dict(color=COLORS['primary'], width=3), # Use COLORS
        hovertemplate='<b>RSI</b><br>' +
                     'Date: %{customdata}<br>' +
                     'RSI: %{y:.2f}<br>' +
                     '<extra></extra>',
        customdata=data_copy['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
    ))
    fig.add_hline(y=70, line_dash="dash", line_color=COLORS['danger']) # Use COLORS
    fig.add_hline(y=30, line_dash="dash", line_color=COLORS['success']) # Use COLORS
    
    # Configure x-axis
    n_points = len(data_copy)
    if n_points > 20:
        step = max(1, n_points // 10)
        tick_indices = list(range(0, n_points, step))
        if tick_indices[-1] != n_points - 1:
            tick_indices.append(n_points - 1)
    else:
        tick_indices = list(range(n_points))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d') for i in tick_indices]
    
    fig.update_layout(
        title="RSI (14)", 
        height=300,
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor=COLORS['bg_tertiary']), # Use COLORS
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            type='linear',
            showgrid=True,
            gridcolor=COLORS['bg_tertiary'] # Use COLORS
        )
    )
    
    return fig

def create_macd_chart(data):
    """Create MACD chart without gaps"""
    data_copy = data.copy()
    data_copy['x_index'] = range(len(data_copy))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['MACD'],
        name='MACD', line=dict(color=COLORS['info']), # Use COLORS
        hovertemplate='<b>MACD</b><br>' +
                     'Date: %{customdata}<br>' +
                     'MACD: %{y:.4f}<br>' +
                     '<extra></extra>',
        customdata=data_copy['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
    ))
    fig.add_trace(go.Scatter(
        x=data_copy['x_index'], y=data_copy['MACD_Signal'],
        name='Signal', line=dict(color=COLORS['danger']), # Use COLORS
        hovertemplate='<b>Signal</b><br>' +
                     'Date: %{customdata}<br>' +
                     'Signal: %{y:.4f}<br>' +
                     '<extra></extra>',
        customdata=data_copy['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
    ))
    
    if 'MACD_Hist' in data_copy.columns:
        colors_macd = [COLORS['success'] if x >= 0 else COLORS['danger'] for x in data_copy['MACD_Hist']] # Use COLORS
        fig.add_trace(go.Bar(
            x=data_copy['x_index'], y=data_copy['MACD_Hist'],
            name='Histogram', marker_color=colors_macd, opacity=0.6,
            hovertemplate='<b>Histogram</b><br>' +
                         'Date: %{customdata}<br>' +
                         'Hist: %{y:.4f}<br>' +
                         '<extra></extra>',
            customdata=data_copy['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
        ))
    
    # Configure x-axis
    n_points = len(data_copy)
    if n_points > 20:
        step = max(1, n_points // 10)
        tick_indices = list(range(0, n_points, step))
        if tick_indices[-1] != n_points - 1:
            tick_indices.append(n_points - 1)
    else:
        tick_indices = list(range(n_points))
    
    tick_values = [data_copy.iloc[i]['x_index'] for i in tick_indices]
    tick_texts = [data_copy.iloc[i]['Datetime'].strftime('%m/%d') for i in tick_indices]
    
    fig.update_layout(
        title="MACD", 
        height=300,
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_texts,
            type='linear',
            showgrid=True,
            gridcolor=COLORS['bg_tertiary'] # Use COLORS
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['bg_tertiary'] # Use COLORS
        )
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