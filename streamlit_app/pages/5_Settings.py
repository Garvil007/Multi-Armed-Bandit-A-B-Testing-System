import streamlit as st
from utils.api_client import get_api_client
from utils.helpers import SessionState
from config import config
import os

st.set_page_config(
    page_title="Settings - MAB Platform",
    page_icon="⚙️",
    layout="wide"
)

SessionState.initialize()
api_client = get_api_client(config.API_BASE_URL)

st.title("⚙️ Settings & Configuration")

# Tabs for different settings
tab1, tab2, tab3, tab4 = st.tabs(["🔌 API", "🎨 Display", "📊 Monitoring", "ℹ️ About"])

# Tab 1: API Settings
with tab1:
    st.header("API Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Connection Settings")
        
        api_url = st.text_input(
            "API Base URL",
            value=config.API_BASE_URL,
            help="URL of the MAB API backend"
        )
        
        if st.button("🔄 Test Connection", use_container_width=True):
            test_client = get_api_client(api_url)
            if test_client.health_check():
                st.success("✅ Connection successful!")
            else:
                st.error("❌ Connection failed")
        
        st.markdown("---")
        
        st.subheader("API Endpoints")
        
        endpoints = {
            "Health Check": f"{api_url}/health",
            "Create Experiment": f"{api_url}/experiments",
            "List Experiments": f"{api_url}/experiments",
            "Select Arm": f"{api_url}/select",
            "Update Reward": f"{api_url}/update",
            "Get Stats": f"{api_url}/experiments/{{name}}/stats",
            "Metrics": f"{api_url}/metrics"
        }
        
        for name, endpoint in endpoints.items():
            st.code(f"{name}: {endpoint}", language="text")
    
    with col2:
        st.subheader("Connection Status")
        
        if api_client.health_check():
            st.success("✅ Connected")
            
            # Show API info
            try:
                response = api_client.session.get(f"{config.API_BASE_URL}/")
                info = response.json()
                
                st.write("**API Information:**")
                st.json(info)
            except:
                pass
        else:
            st.error("❌ Disconnected")
            
            st.warning("""
            **Troubleshooting:**
            1. Ensure API is running
            2. Check the URL is correct
            3. Verify firewall settings
            4. Check Docker containers
            """)
        
        st.markdown("---")
        
        st.subheader("Quick Actions")
        
        if st.button("📚 View API Docs", use_container_width=True):
            st.markdown(f"[Open API Documentation]({api_url}/docs)")
        
        if st.button("🔍 View Metrics", use_container_width=True):
            st.markdown(f"[Open Prometheus Metrics]({api_url}/metrics)")

# Tab 2: Display Settings
with tab2:
    st.header("Display Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Chart Settings")
        
        theme = st.selectbox(
            "Chart Theme",
            options=["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
            index=1,
            help="Visual theme for charts"
        )
        
        animation_speed = st.slider(
            "Animation Speed",
            min_value=0,
            max_value=100,
            value=50,
            help="Speed of chart animations (0 = instant)"
        )
        
        show_grid = st.checkbox("Show Grid Lines", value=True)
        show_legend = st.checkbox("Show Legends", value=True)
        
        st.markdown("---")
        
        st.subheader("Refresh Rates")
        
        metrics_refresh = st.slider(
            "Metrics Refresh (seconds)",
            min_value=1,
            max_value=60,
            value=config.METRICS_REFRESH_INTERVAL,
            help="How often to refresh metrics"
        )
        
        stats_refresh = st.slider(
            "Stats Refresh (seconds)",
            min_value=5,
            max_value=120,
            value=config.STATS_REFRESH_INTERVAL,
            help="How often to refresh statistics"
        )
    
    with col2:
        st.subheader("Preview")
        
        import plotly.graph_objects as go
        
        # Sample chart with current settings
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[1, 3, 2, 4, 3],
            mode='lines+markers',
            name='Sample Data'
        ))
        
        fig.update_layout(
            template=theme,
            showlegend=show_legend,
            xaxis=dict(showgrid=show_grid),
            yaxis=dict(showgrid=show_grid),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("This is how your charts will look with current settings")
    
    st.markdown("---")
    
    if st.button("💾 Save Display Settings", use_container_width=True):
        # Save to session state
        SessionState.set('chart_theme', theme)
        SessionState.set('animation_speed', animation_speed)
        SessionState.set('show_grid', show_grid)
        SessionState.set('show_legend', show_legend)
        SessionState.set('metrics_refresh', metrics_refresh)
        SessionState.set('stats_refresh', stats_refresh)
        
        st.success("✅ Settings saved!")

# Tab 3: Monitoring
with tab3:
    st.header("Monitoring & Observability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Prometheus")
        
        prometheus_url = st.text_input(
            "Prometheus URL",
            value="http://localhost:9090",
            help="URL of Prometheus instance"
        )
        
        if st.button("🔍 Open Prometheus", use_container_width=True):
            st.markdown(f"[Open Prometheus]({prometheus_url})")
        
        st.markdown("---")
        
        st.write("**Key Metrics to Monitor:**")
        st.code("""
- mab_arm_selections_total
- mab_rewards_total
- mab_reward_value
- mab_active_experiments
        """)
        
        st.markdown("---")
        
        st.subheader("📊 Sample Queries")
        
        st.code("""
# Total selections per arm
sum by (arm) (mab_arm_selections_total)

# Reward rate
rate(mab_rewards_total[5m])

# Average reward value
histogram_quantile(0.5, 
  rate(mab_reward_value_bucket[5m]))
        """, language="promql")
    
    with col2:
        st.subheader("📈 Grafana")
        
        grafana_url = st.text_input(
            "Grafana URL",
            value="http://localhost:3000",
            help="URL of Grafana instance"
        )
        
        if st.button("📊 Open Grafana", use_container_width=True):
            st.markdown(f"[Open Grafana]({grafana_url})")
        
        st.markdown("---")
        
        st.subheader("🧪 MLflow")
        
        mlflow_url = st.text_input(
            "MLflow URL",
            value="http://localhost:5000",
            help="URL of MLflow tracking server"
        )
        
        if st.button("🔬 Open MLflow", use_container_width=True):
            st.markdown(f"[Open MLflow]({mlflow_url})")
        
        st.markdown("---")
        
        st.info("""
        **Setting up MLflow:**
```bash
        mlflow ui --host 0.0.0.0 --port 5000
```
        """)
    
    st.markdown("---")
    
    st.subheader("🚨 Alerts & Notifications")
    
    st.info("Alert configuration coming soon! Will support:")
    st.markdown("""
    - Slack notifications
    - Email alerts
    - Webhook integrations
    - PagerDuty integration
    """)

# Tab 4: About
with tab4:
    st.header("About MAB A/B Testing Platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📚 Documentation")
        
        st.markdown("""
        ### What is Multi-Armed Bandit?
        
        Multi-Armed Bandit (MAB) is a machine learning framework for optimizing decisions 
        under uncertainty. Unlike traditional A/B testing which splits traffic equally, 
        MAB algorithms dynamically allocate more traffic to better-performing variants.
        
        ### Key Benefits
        
        - **Faster Optimization**: Converges to best variant quicker than A/B tests
        - **Lower Regret**: Minimizes opportunity cost during testing
        - **Automatic Adaptation**: Adjusts to changing conditions in real-time
        - **No Fixed Duration**: Can run continuously
        
        ### Algorithms Supported
        
        1. **Epsilon-Greedy**: Simple and effective
           - Explores with probability ε
           - Exploits best arm with probability 1-ε
           
        2. **Thompson Sampling**: Bayesian approach
           - Samples from posterior distributions
           - Naturally balances exploration/exploitation
           
        3. **Upper Confidence Bound (UCB)**: Optimistic strategy
           - Selects arm with highest upper confidence bound
           - Theoretical performance guarantees
        
        ### Use Cases
        
        - Website A/B testing (headlines, CTAs, layouts)
        - Content recommendation
        - Ad placement optimization
        - Email campaign optimization
        - Pricing experiments
        - Feature rollouts
        """)
        
        st.markdown("---")
        
        st.subheader("📖 Resources")
        
        st.markdown("""
        - [Sutton & Barto - Reinforcement Learning](http://incompleteideas.net/book/the-book.html)
        - [Bandit Algorithms Book](https://tor-lattimore.com/downloads/book/book.pdf)
        - [Multi-Armed Bandits on Wikipedia](https://en.wikipedia.org/wiki/Multi-armed_bandit)
        - [FastAPI Documentation](https://fastapi.tiangolo.com/)
        - [Streamlit Documentation](https://docs.streamlit.io/)
        """)
    
    with col2:
        st.subheader("ℹ️ System Info")
        
        st.write("**Version**: 1.0.0")
        st.write("**Build**: 2024-01-15")
        
        st.markdown("---")
        
        st.subheader("🛠️ Tech Stack")
        
        st.markdown("""
        **Backend:**
        - FastAPI
        - Python 3.10+
        - NumPy, SciPy
        
        **Frontend:**
        - Streamlit
        - Plotly
        - Pandas
        
        **MLOps:**
        - MLflow
        - Prometheus
        - Grafana
        - Docker
        """)
        
        st.markdown("---")
        
        st.subheader("👥 Contributors")
        
        st.markdown("""
        Built with ❤️ for learning
        Reinforcement Learning and MLOps
        
        **Author**: [Your Name]
        **GitHub**: [Your Repo]
        **License**: MIT
        """)
        
        st.markdown("---")
        
        st.subheader("🐛 Report Issues")
        
        if st.button("Report a Bug", use_container_width=True):
            st.info("Open an issue on GitHub")
        
        if st.button("Request Feature", use_container_width=True):
            st.info("Submit a feature request")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>MAB A/B Testing Platform v1.0.0</p>
    <p>🎰 Optimize smarter, not harder</p>
</div>
""", unsafe_allow_html=True)