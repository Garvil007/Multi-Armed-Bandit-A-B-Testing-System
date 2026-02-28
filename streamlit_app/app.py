import streamlit as st
from config import config
from utils.api_client import get_api_client
from utils.helpers import SessionState

# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
SessionState.initialize()

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/_static/favicon.png", width=50)
    st.title("🎰 MAB Platform")
    
    # API Connection Status
    st.markdown("---")
    st.subheader("🔌 API Connection")
    
    api_client = get_api_client(config.API_BASE_URL)
    
    if api_client.health_check():
        st.success("✅ Connected")
        SessionState.set('api_connected', True)
    else:
        st.error("❌ Disconnected")
        st.warning(f"Cannot connect to API at {config.API_BASE_URL}")
        SessionState.set('api_connected', False)
    
    # Quick Stats
    if SessionState.get('api_connected'):
        st.markdown("---")
        st.subheader("📊 Quick Stats")
        
        try:
            experiments = api_client.list_experiments()
            st.metric("Active Experiments", len(experiments))
            
            if experiments:
                total_pulls = sum(exp.get('total_pulls', 0) for exp in experiments)
                st.metric("Total Interactions", total_pulls)
        except:
            st.info("No experiments yet")
    
    # Navigation
    st.markdown("---")
    st.subheader("📍 Navigation")
    st.info("""
    **Pages:**
    - 🏠 Home: Overview & Introduction
    - 🧪 Experiments: Create & Manage
    - 📊 Analytics: Deep Dive Insights  
    - 🎯 Simulate: Run Test Scenarios
    - ⚙️ Settings: Configuration
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        <p>MAB A/B Testing Platform v1.0</p>
        <p>Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("<h1 class='main-header'>🎰 Multi-Armed Bandit A/B Testing Platform</h1>", unsafe_allow_html=True)

st.markdown("---")

# Welcome section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <h3>🚀 Quick Start</h3>
        <p>Create experiments in minutes with our intuitive interface</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <h3>📈 Real-time Analytics</h3>
        <p>Monitor performance with live dashboards and metrics</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <h3>🤖 Smart Algorithms</h3>
        <p>Leverage state-of-the-art MAB algorithms for optimization</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Feature overview
st.header("✨ Platform Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧪 Experiment Management")
    st.markdown("""
    - Create and manage multiple experiments
    - Support for 3 MAB algorithms
    - Real-time arm selection and reward updates
    - Experiment versioning and state management
    """)
    
    st.subheader("📊 Advanced Analytics")
    st.markdown("""
    - Cumulative reward tracking
    - Regret analysis and optimization
    - Confidence interval visualization
    - Arm performance comparison
    """)

with col2:
    st.subheader("🎯 Simulation Tools")
    st.markdown("""
    - Test scenarios with custom parameters
    - Batch simulation for performance testing
    - Compare algorithm performance
    - Export results for further analysis
    """)
    
    st.subheader("⚙️ Production Ready")
    st.markdown("""
    - RESTful API integration
    - Docker containerization
    - Prometheus metrics
    - MLflow experiment tracking
    """)

st.markdown("---")

# Getting Started
st.header("🎯 Getting Started")

with st.expander("📖 Quick Tutorial", expanded=False):
    st.markdown("""
    ### Step 1: Create an Experiment
    Navigate to the **🧪 Experiments** page and click "Create New Experiment"
    
    ### Step 2: Configure Your Test
    - Choose your arms (variants to test)
    - Select an algorithm (Epsilon-Greedy, Thompson Sampling, or UCB)
    - Set algorithm parameters
    
    ### Step 3: Run Simulations
    Use the **🎯 Simulate** page to test your experiment with synthetic data
    
    ### Step 4: Monitor Performance
    Track results in real-time on the **📊 Analytics** page
    
    ### Step 5: Integrate with Your App
    Use the API endpoints to integrate with your production application
    """)

with st.expander("🧠 Algorithm Comparison", expanded=False):
    st.markdown("""
    | Algorithm | Best For | Pros | Cons |
    |-----------|----------|------|------|
    | **Epsilon-Greedy** | Quick convergence | Simple, fast | Fixed exploration |
    | **Thompson Sampling** | Binary rewards | Adaptive, Bayesian | Complex math |
    | **UCB** | Theoretical guarantees | Deterministic | Slower convergence |
    """)

# Call to action
st.markdown("---")
st.success("👈 **Start by creating your first experiment in the Experiments page!**")

if not SessionState.get('api_connected'):
    st.error("""
    ⚠️ **API Not Connected!**
    
    Please ensure the FastAPI backend is running:
```bash
    uvicorn src.api.app:app --reload
```
    """)