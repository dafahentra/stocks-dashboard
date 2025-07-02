import streamlit as st

# Color constants for charts and components
COLORS = {
    'primary': '#6366f1',
    'secondary': '#10b981',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'info': '#3b82f6',
    'text_primary': '#f8fafc',
    'text_secondary': '#cbd5e1',
    'text_muted': '#94a3b8',
    'bg_primary': '#0f172a',
    'bg_secondary': '#1e293b',
    'bg_tertiary': '#334155',
    'border': '#334155',
}

def apply_minimal_style():
    """Apply minimal custom styling only for elements not handled by config.toml"""
    
    st.markdown("""
    <style>
        /* Hide Streamlit branding elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)