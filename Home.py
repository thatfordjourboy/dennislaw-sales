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

# Custom CSS
st.markdown("""
    <style>
    .welcome-header {
        text-align: center;
        padding: 2rem 0;
        color: #1e293b;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        color: #334155;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .feature-text {
        color: #64748b;
    }
    .getting-started {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 8px;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Welcome Header
st.markdown("""
    <div class="welcome-header">
        <h1>Welcome to Dennislaw Sales Analysis Dashboard</h1>
        <p style="font-size: 1.2rem; color: #64748b;">
            Your comprehensive solution for analyzing subscription sales data
        </p>
    </div>
""", unsafe_allow_html=True)

# Main Features Section
st.markdown("### 📈 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Interactive Visualizations</div>
            <div class="feature-text">
                Explore dynamic charts and graphs that bring your sales data to life.
                Track monthly trends, compare year-over-year performance, and analyze package distributions.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Performance Metrics</div>
            <div class="feature-text">
                Monitor key performance indicators including revenue growth, subscription trends,
                and package performance with real-time calculations and comparisons.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <div class="feature-title">Flexible Filtering</div>
            <div class="feature-text">
                Customize your analysis with powerful filtering options by year, month,
                and subscription packages to focus on what matters most.
            </div>
        </div>
    """, unsafe_allow_html=True)

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
