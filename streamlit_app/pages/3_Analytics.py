import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.api_client import get_api_client
from utils.visualizations import (
    create_arm_comparison,
    create_confidence_intervals,
    create_metrics_summary
)
from utils.helpers import SessionState
from config import config
import pandas as pd

st.set_page_config(
    page_title="Analytics - MAB Platform",
    page_icon="📊",
    layout="wide"
)

# Auto-refresh every 10 seconds
count = st_autorefresh(interval=config.STATS_REFRESH_INTERVAL * 1000, key="analytics_refresh")

# Initialize
SessionState.initialize()
api_client = get_api_client(config.API_BASE_URL)

st.title("📊 Real-Time Analytics Dashboard")

# Check API connection
if not api_client.health_check():
    st.error("❌ Cannot connect to API")
    st.stop()

# Experiment selector
try:
    experiments = api_client.list_experiments()
    
    if not experiments:
        st.warning("No experiments available. Create one first!")
        if st.button("➕ Create Experiment"):
            st.switch_page("pages/2_🧪_Experiments.py")
        st.stop()
    
    # Get current experiment from session state or default to first
    current_exp = SessionState.get('current_experiment')
    if current_exp not in [e['name'] for e in experiments]:
        current_exp = experiments[0]['name']
    
    selected_exp = st.selectbox(
        "Select Experiment",
        options=[e['name'] for e in experiments],
        index=[e['name'] for e in experiments].index(current_exp),
        key="analytics_exp_selector"
    )
    
    SessionState.set('current_experiment', selected_exp)
    
    # Get experiment stats
    with st.spinner("Loading analytics..."):
        stats = api_client.get_experiment_stats(selected_exp)
    
    # Display metrics
    st.markdown("---")
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Pulls",
            f"{stats['total_pulls']:,}",
            help="Total number of arm selections"
        )
    
    with col2:
        st.metric(
            "Avg Reward",
            f"{stats['average_reward']:.4f}",
            help="Average reward across all pulls"
        )
    
    with col3:
        st.metric(
            "Total Reward",
            f"{stats['total_reward']:.2f}",
            help="Cumulative reward received"
        )
    
    with col4:
        best_arm_idx = stats['arm_values'].index(max(stats['arm_values']))
        st.metric(
            "Best Arm",
            stats['arm_names'][best_arm_idx],
            help="Arm with highest estimated value"
        )
    
    with col5:
        exploration_rate = 1 - (max(stats['arm_counts']) / max(stats['total_pulls'], 1))
        st.metric(
            "Exploration Rate",
            f"{exploration_rate:.2%}",
            help="Rate of exploring sub-optimal arms"
        )
    
    st.markdown("---")
    
    # Main visualizations
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🎯 Arms Comparison", "📊 Detailed Stats"])
    
    with tab1:
        st.subheader("Performance Overview")
        
        # Arm comparison
        fig = create_arm_comparison(stats)
        st.plotly_chart(fig, use_container_width=True)
        
        # Confidence intervals
        st.subheader("Confidence Intervals (95%)")
        fig_ci = create_confidence_intervals(stats)
        st.plotly_chart(fig_ci, use_container_width=True)
    
    with tab2:
        st.subheader("Arms Detailed Comparison")
        
        # Create detailed DataFrame
        arm_data = []
        for i, name in enumerate(stats['arm_names']):
            arm_data.append({
                "Arm": name,
                "Pulls": stats['arm_counts'][i],
                "% of Total": f"{100 * stats['arm_counts'][i] / max(stats['total_pulls'], 1):.2f}%",
                "Avg Reward": f"{stats['arm_values'][i]:.4f}",
                "Total Reward": f"{stats['arm_values'][i] * stats['arm_counts'][i]:.2f}",
                "Rank": ""
            })
        
        df = pd.DataFrame(arm_data)
        df = df.sort_values("Avg Reward", ascending=False)
        df['Rank'] = range(1, len(df) + 1)
        
        # Color code by rank
        def highlight_rank(row):
            if row['Rank'] == 1:
                return ['background-color: #d4edda'] * len(row)
            elif row['Rank'] == len(df):
                return ['background-color: #f8d7da'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df.style.apply(highlight_rank, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Statistical tests
        st.subheader("Statistical Significance")
        
        if stats['total_pulls'] >= 100:
            st.success("✅ Sufficient data collected for statistical analysis")
            
            # Simple z-test between best and second-best
            sorted_arms = sorted(
                [(i, v, c) for i, (v, c) in enumerate(zip(stats['arm_values'], stats['arm_counts']))],
                key=lambda x: x[1],
                reverse=True
            )
            
            if len(sorted_arms) >= 2:
                best = sorted_arms[0]
                second = sorted_arms[1]
                
                st.write(f"**Best Arm:** {stats['arm_names'][best[0]]} (value: {best[1]:.4f})")
                st.write(f"**Second Best:** {stats['arm_names'][second[0]]} (value: {second[1]:.4f})")
                st.write(f"**Difference:** {abs(best[1] - second[1]):.4f}")
        else:
            remaining = 100 - stats['total_pulls']
            st.info(f"ℹ️ Need {remaining} more pulls for reliable statistical analysis")
    
    with tab3:
        st.subheader("Detailed Statistics")
        
        # Algorithm-specific stats
        st.write("**Algorithm Information:**")
        st.write(f"- Type: {stats['algorithm']}")
        
        if 'epsilon' in stats:
            st.write(f"- Epsilon: {stats['epsilon']}")
        if 'c' in stats:
            st.write(f"- Confidence Parameter (c): {stats['c']}")
        if 'alpha' in stats and 'beta' in stats:
            st.write("**Thompson Sampling Parameters:**")
            beta_df = pd.DataFrame({
                "Arm": stats['arm_names'],
                "Alpha (successes)": stats['alpha'],
                "Beta (failures)": stats['beta']
            })
            st.dataframe(beta_df, use_container_width=True)
        
        # Raw JSON
        with st.expander("📄 Raw JSON Data"):
            st.json(stats)
    
    # Export functionality
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as CSV
        csv_data = pd.DataFrame({
            "arm": stats['arm_names'],
            "pulls": stats['arm_counts'],
            "avg_reward": stats['arm_values']
        }).to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{selected_exp}_stats.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export as JSON
        import json
        json_data = json.dumps(stats, indent=2)
        
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{selected_exp}_stats.json",
            mime="application/json"
        )

except Exception as e:
    st.error(f"Error loading analytics: {str(e)}")
    st.exception(e)