import streamlit as st
from utils import init_session_state

# Initialize session state
init_session_state()

# Page config
st.set_page_config(
    page_title="Dennislaw Sales Analysis",
    page_icon="📊",
    layout="wide"
)

# Page content
st.title("Welcome to Dennislaw Sales Analysis")

# Add your home page content here
st.markdown("""
    ### Getting Started
    1. Use the sidebar to navigate between different analysis views
    2. Upload your sales data in the Solo Analysis page
    3. Explore trends and insights through interactive visualizations
""")

# You can add more sections, metrics, or welcome content here
