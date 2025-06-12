"""
Dark Modern Design Configuration for Stock Dashboard
Elegant dark theme with hidden Streamlit UI elements
"""

import streamlit as st

# Color Palette - Dark Modern Theme
COLORS = {
    # Primary colors
    'primary': '#6366f1',           # Indigo
    'primary_dark': '#4f46e5',     # Darker indigo
    'secondary': '#10b981',         # Emerald
    'accent': '#f59e0b',           # Amber
    
    # Background colors
    'bg_primary': '#0f172a',       # Very dark blue
    'bg_secondary': '#1e293b',     # Dark slate
    'bg_tertiary': '#334155',      # Medium slate
    'bg_card': '#1e293b',          # Card background
    
    # Text colors
    'text_primary': '#f8fafc',     # Almost white
    'text_secondary': '#cbd5e1',   # Light gray
    'text_muted': '#94a3b8',       # Muted gray
    
    # Border and accent colors
    'border': '#334155',           # Subtle border
    'success': '#10b981',          # Green
    'danger': '#ef4444',           # Red
    'warning': '#f59e0b',          # Amber
    'info': '#3b82f6',             # Blue
    
    # Chart colors
    'chart_primary': '#6366f1',
    'chart_secondary': '#10b981',
    'chart_tertiary': '#f59e0b',
    'chart_quaternary': '#ef4444',
    'chart_quinary': '#8b5cf6',
}

# Chart color schemes
CHART_COLORS = {
    'indicators': [COLORS['chart_primary'], COLORS['chart_secondary'], 
                  COLORS['chart_tertiary'], COLORS['chart_quaternary'], 
                  COLORS['chart_quinary']],
    'candlestick_up': COLORS['success'],
    'candlestick_down': COLORS['danger'],
    'volume_up': COLORS['success'],
    'volume_down': COLORS['danger'],
    'bollinger': 'rgba(99, 102, 241, 0.3)',
    'rsi_overbought': COLORS['danger'],
    'rsi_oversold': COLORS['success'],
    'rsi_neutral': COLORS['chart_primary']
}

def apply_dark_theme():
    """Apply comprehensive dark theme with hidden Streamlit UI"""
    
    st.markdown(f"""
    <style>
        /* Hide Streamlit UI Elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        .stDecoration {{display: none;}}
        
        /* Hide "Made with Streamlit" */
        .css-hi6a2p {{display: none;}}
        .css-9s5bis {{display: none;}}
        .css-1dp5vir {{display: none;}}
        
        /* Hide hamburger menu */
        .css-14xtw13 {{display: none;}}
        
        /* Global Styles */
        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg_primary']} 0%, #0c1220 100%);
            color: {COLORS['text_primary']};
        }}
        
        /* Sidebar Styling */
        .css-1d391kg {{
            background: linear-gradient(180deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_primary']} 100%);
            border-right: 1px solid {COLORS['border']};
        }}
        
        .css-17eq0hr {{
            background: transparent;
        }}
        
        /* Main Header */
        .main-header {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 50%, #8b5cf6 100%);
            color: {COLORS['text_primary']};
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}
        
        .main-header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .main-header p {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin: 0;
        }}
        
        /* Metric Cards */
        .css-1r6slb0 {{
            background: linear-gradient(145deg, {COLORS['bg_card']} 0%, {COLORS['bg_tertiary']} 100%);
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
        }}
        
        .css-1r6slb0:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
        }}
        
        /* Metric Values */
        [data-testid="metric-container"] {{
            background: linear-gradient(145deg, {COLORS['bg_card']} 0%, rgba(51, 65, 85, 0.8) 100%);
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 6px 24px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}
        
        [data-testid="metric-container"]:hover {{
            border-color: {COLORS['primary']};
            transform: translateY(-1px);
            transition: all 0.3s ease;
        }}
        
        [data-testid="metric-container"] > div {{
            color: {COLORS['text_primary']};
        }}
        
        /* Tabs Styling */
        
        .stTabs {{
            margin-bottom: 2rem;
            margin-top: 1rem;
    }}
      
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            background: {COLORS['bg_secondary']};
            border-radius: 12px;
            padding: 8px;
            border: 1px solid {COLORS['border']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 8px;
            color: {COLORS['text_secondary']};
            border: none;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(99, 102, 241, 0.1);
            color: {COLORS['text_primary']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%) !important;
            color: {COLORS['text_primary']} !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}
        
        /* Input Fields */
        .stTextInput > div > div > input {{
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
            border-radius: 8px;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }}
        
        /* Selectbox */
        .stSelectbox > div > div {{
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        }}
        
        .stSelectbox > div > div > div {{
            color: {COLORS['text_primary']};
        }}
        
        /* Multiselect */
        .stMultiSelect > div > div {{
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        }}
        
        /* Checkbox */
        .stCheckbox > label {{
            color: {COLORS['text_secondary']};
        }}
        
        .stCheckbox > label:hover {{
            color: {COLORS['text_primary']};
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }}
        
        /* Sidebar Headers */
        .css-1d391kg h2, .css-1d391kg h3 {{
            color: {COLORS['text_primary']};
            border-bottom: 2px solid {COLORS['primary']};
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        /* Sidebar Elements */
        .css-1d391kg .stSelectbox label,
        .css-1d391kg .stTextInput label,
        .css-1d391kg .stMultiSelect label {{
            color: {COLORS['text_secondary']};
            font-weight: 500;
        }}
        
        /* Dataframe Styling */
        .stDataFrame {{
            background: {COLORS['bg_card']};
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            overflow: hidden;
        }}
        
        /* Success/Error Messages */
        .stAlert {{
            border-radius: 10px;
            border: 1px solid;
        }}
        
        .stSuccess {{
            background: rgba(16, 185, 129, 0.1);
            border-color: {COLORS['success']};
            color: {COLORS['success']};
        }}
        
        .stError {{
            background: rgba(239, 68, 68, 0.1);
            border-color: {COLORS['danger']};
            color: {COLORS['danger']};
        }}
        
        .stWarning {{
            background: rgba(245, 158, 11, 0.1);
            border-color: {COLORS['warning']};
            color: {COLORS['warning']};
        }}
        
        .stInfo {{
            background: rgba(59, 130, 246, 0.1);
            border-color: {COLORS['info']};
            color: {COLORS['info']};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: {COLORS['bg_tertiary']};
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
        }}
        
        .streamlit-expanderContent {{
            background: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        
        /* Spinner */
        .stSpinner > div {{
            border-top-color: {COLORS['primary']} !important;
        }}
        
        /* Caption */
        .css-1v0mbdj {{
            color: {COLORS['text_muted']};
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_secondary']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['primary']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['primary_dark']};
        }}
        
        /* Animation for smooth transitions */
        * {{
            transition: all 0.3s ease;
        }}
        
        /* Glassmorphism effect for cards */
        .glass-card {{
            background: rgba(30, 41, 59, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
        }}
        
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create elegant header with dark theme"""
    st.markdown('''
    <div class="main-header">
        <h1>Stock Dashboard</h1>
        <p>Comprehensive Stocks Report & Trend Analytics</p>
    </div>
    ''', unsafe_allow_html=True)

def get_chart_template():
    """Get dark chart template configuration"""
    # This function is not currently used in stocks_dashboard.py
    # but could be used to apply a Plotly theme directly to figures.
    return {
        'layout': {
            'template': 'plotly_dark',
            'paper_bgcolor': COLORS['bg_primary'],
            'plot_bgcolor': COLORS['bg_card'],
            'font': {'color': COLORS['text_primary']},
            'colorway': CHART_COLORS['indicators'],
            'gridcolor': COLORS['border'],
            'zerolinecolor': COLORS['border']
        }
    }