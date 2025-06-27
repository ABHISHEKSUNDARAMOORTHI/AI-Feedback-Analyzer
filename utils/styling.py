import streamlit as st

def apply_base_styles(dark_mode=True):
    """
    Applies base CSS styles for the Streamlit app, supporting dark/light mode.
    Includes font, color variables, and general component styling.
    """
    # Define color palette based on dark/light mode
    if dark_mode:
        # Dark Mode Colors
        bg_primary = "#0f172a"  # Dark blue-gray for main background
        bg_secondary = "#1a202c" # Slightly lighter dark for components
        text_color = "#e2e8f0"   # Light gray for text
        header_color = "#38bdf8" # Sky blue for headers (accent)
        accent_blue_light = "#0ea5e9" # Lighter blue for highlights
        border_color = "#475569" # Slate gray for borders
    else:
        # Light Mode Colors
        bg_primary = "#FFFFFF"   # White for main background
        bg_secondary = "#F0F2F6" # Light gray for components
        text_color = "#111827"   # Dark gray for text
        header_color = "#2196F3" # Google Blue for headers
        accent_blue_light = "#64B5F6" # Lighter blue for highlights
        border_color = "#D1D5DB" # Light gray for borders

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    :root {{
        --bg-primary: {bg_primary};
        --bg-secondary: {bg_secondary};
        --text-color: {text_color};
        --header-color: {header_color};
        --accent-blue-light: {accent_blue_light};
        --border-color: {border_color};
        --success-color: #28a745; /* Bootstrap green */
        --info-color: #17a2b8; /* Bootstrap cyan */
        --warning-color: #ffc107; /* Bootstrap yellow */
        --error-color: #dc3545; /* Bootstrap red */
    }}

    body {{
        font-family: 'Inter', sans-serif;
        color: var(--text-color);
        background-color: var(--bg-primary);
    }}

    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-color);
    }}

    /* Main container padding adjustments */
    .st-emotion-cache-nahz7x {{ /* Corresponds to .stApp > header + div */
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }}

    /* Streamlit widgets styling */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--header-color);
        font-weight: 600;
    }}

    .stButton > button {{
        background-color: var(--accent-blue-light);
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: #0c8ad9; /* Slightly darker accent */
    }}

    .stFileUploader label {{
        color: var(--text-color);
        font-weight: 600;
    }}
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {{
        background-color: var(--bg-secondary);
        border: 1px dashed var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-color);
    }}
    .stFileUploader div[data-testid="stFileUploaderDropzone"] svg {{
        fill: var(--text-color);
    }}

    /* Text areas and inputs */
    .stTextInput div[data-baseweb="input"] input,
    .stTextArea div[data-baseweb="textarea"] textarea {{
        background-color: var(--bg-secondary);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
    }}
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {{
        border-radius: 0.5rem;
    }}
    .stAlert.info {{
        background-color: rgba(23, 162, 184, 0.1); /* 10% opacity */
        color: var(--info-color);
        border-left: 5px solid var(--info-color);
    }}
    .stAlert.success {{
        background-color: rgba(40, 167, 69, 0.1);
        color: var(--success-color);
        border-left: 5px solid var(--success-color);
    }}
    .stAlert.warning {{
        background-color: rgba(255, 193, 7, 0.1);
        color: var(--warning-color);
        border-left: 5px solid var(--warning-color);
    }}
    .stAlert.error {{
        background-color: rgba(220, 53, 69, 0.1);
        color: var(--error-color);
        border-left: 5px solid var(--error-color);
    }}

    /* General markdown elements */
    p {{
        line-height: 1.6;
    }}
    
    </style>
    """, unsafe_allow_html=True)

# Function to toggle the theme (called in app.py)
def set_theme_js(dark_mode):
    """Injects JavaScript to set theme in sessionStorage and body class."""
    theme_name = 'dark' if dark_mode else 'light'
    st.markdown(f"""
        <script>
            sessionStorage.setItem('streamlit_theme', '{theme_name}');
            document.body.classList.toggle('light-theme', !{dark_mode});
        </script>
    """, unsafe_allow_html=True)