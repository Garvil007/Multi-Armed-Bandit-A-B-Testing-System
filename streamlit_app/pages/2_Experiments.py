import streamlit as st
from utils.api_client import get_api_client
from utils.helpers import SessionState, validate_experiment_name, get_algorithm_emoji
from config import config
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Experiments - MAB Platform",
    page_icon="🧪",
    layout="wide"
)

# Initialize
SessionState.initialize()
api_client = get_api_client(config.API_BASE_URL)

st.title("🧪 Experiment Management")

# Check API connection
if not api_client.health_check():
    st.error("❌ Cannot connect to API. Please ensure the backend is running.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Experiments", "➕ Create New", "🗑️ Manage"])

# Tab 1: List Experiments
with tab1:
    st.header("Active Experiments")
    
    try:
        experiments = api_client.list_experiments()
        
        if not experiments:
            st.info("No experiments found. Create your first experiment in the 'Create New' tab!")
        else:
            # Create DataFrame
            df = pd.DataFrame(experiments)
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Experiments", len(experiments))
            with col2:
                total_pulls = df['total_pulls'].sum()
                st.metric("Total Interactions", f"{total_pulls:,}")
            with col3:
                active = len(df[df['total_pulls'] > 0])
                st.metric("Active", active)
            with col4:
                inactive = len(df[df['total_pulls'] == 0])
                st.metric("Inactive", inactive)
            
            st.markdown("---")
            
            # Display experiments
            for idx, exp in enumerate(experiments):
                with st.expander(
                    f"{get_algorithm_emoji(exp['algorithm'])} {exp['name']} - "
                    f"{exp['algorithm'].replace('_', ' ').title()} "
                    f"({exp['total_pulls']} pulls)",
                    expanded=(idx == 0)
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Details:**")
                        st.write(f"- Algorithm: {exp['algorithm'].replace('_', ' ').title()}")
                        st.write(f"- Created: {exp['created_at']}")
                        st.write(f"- Total Pulls: {exp['total_pulls']}")
                        
                        # Get full stats
                        if st.button(f"View Stats", key=f"stats_{exp['name']}"):
                            with st.spinner("Loading stats..."):
                                stats = api_client.get_experiment_stats(exp['name'])
                                
                                st.write("**Performance Metrics:**")
                                st.write(f"- Average Reward: {stats['average_reward']:.4f}")
                                st.write(f"- Total Reward: {stats['total_reward']:.2f}")
                                
                                st.write("**Arm Statistics:**")
                                arm_df = pd.DataFrame({
                                    'Arm': stats['arm_names'],
                                    'Pulls': stats['arm_counts'],
                                    'Avg Reward': [f"{v:.4f}" for v in stats['arm_values']]
                                })
                                st.dataframe(arm_df, use_container_width=True)
                    
                    with col2:
                        st.write("**Quick Actions:**")
                        if st.button("📊 View Analytics", key=f"analytics_{exp['name']}"):
                            SessionState.set('current_experiment', exp['name'])
                            st.switch_page("pages/3_📊_Analytics.py")
                        
                        if st.button("🎯 Simulate", key=f"simulate_{exp['name']}"):
                            SessionState.set('current_experiment', exp['name'])
                            st.switch_page("pages/4_🎯_Simulate.py")
    
    except Exception as e:
        st.error(f"Error loading experiments: {str(e)}")

# Tab 2: Create New Experiment
with tab2:
    st.header("Create New Experiment")
    
    with st.form("create_experiment_form"):
        # Experiment name
        exp_name = st.text_input(
            "Experiment Name",
            placeholder="e.g., homepage_banner_test",
            help="Use lowercase letters, numbers, underscores, and hyphens"
        )
        
        # Algorithm selection
        algorithm = st.selectbox(
            "Algorithm",
            options=["epsilon_greedy", "thompson_sampling", "ucb"],
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Choose the MAB algorithm to use"
        )
        
        # Show algorithm info
        st.info(config.ALGORITHM_INFO[algorithm])
        
        # Algorithm-specific parameters
        col1, col2 = st.columns(2)
        
        with col1:
            if algorithm == "epsilon_greedy":
                epsilon = st.slider(
                    "Epsilon (ε)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.1,
                    step=0.05,
                    help="Exploration rate: higher = more exploration"
                )
            elif algorithm == "ucb":
                c = st.slider(
                    "Confidence (c)",
                    min_value=0.1,
                    max_value=5.0,
                    value=2.0,
                    step=0.1,
                    help="Exploration parameter: higher = more exploration"
                )
        
        # Arms configuration
        st.subheader("Configure Arms (Variants)")
        
        num_arms = st.number_input(
            "Number of Arms",
            min_value=2,
            max_value=10,
            value=3,
            help="How many variants do you want to test?"
        )
        
        arms = []
        cols = st.columns(min(num_arms, 3))
        
        for i in range(num_arms):
            col_idx = i % len(cols)
            with cols[col_idx]:
                arm_name = st.text_input(
                    f"Arm {i+1}",
                    value=f"Variant_{chr(65+i)}",
                    key=f"arm_{i}"
                )
                arms.append(arm_name)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create Experiment", use_container_width=True)
        
        if submitted:
            # Validation
            if not validate_experiment_name(exp_name):
                st.error("Invalid experiment name. Use 3+ characters with letters, numbers, _, or -")
            elif len(set(arms)) != len(arms):
                st.error("Arm names must be unique!")
            else:
                try:
                    # Create experiment
                    with st.spinner("Creating experiment..."):
                        result = api_client.create_experiment(
                            name=exp_name,
                            arms=arms,
                            algorithm=algorithm,
                            epsilon=epsilon if algorithm == "epsilon_greedy" else 0.1,
                            c=c if algorithm == "ucb" else 2.0
                        )
                    
                    st.success(f"✅ Experiment '{exp_name}' created successfully!")
                    st.balloons()
                    
                    # Show next steps
                    st.info("""
                    **Next Steps:**
                    1. Go to the 🎯 Simulate tab to test your experiment
                    2. View real-time analytics in the 📊 Analytics tab
                    3. Integrate the API endpoints into your application
                    """)
                    
                    # Show API integration example
                    with st.expander("📝 API Integration Example"):
                        st.code(f"""
# Select arm for user
import requests

response = requests.post(
    "http://localhost:8000/select",
    json={{
        "experiment_name": "{exp_name}",
        "user_id": "user_123"
    }}
)

selection = response.json()
arm_to_show = selection["arm_name"]

# ... show arm to user ...

# Update reward based on user action
requests.post(
    "http://localhost:8000/update",
    json={{
        "experiment_name": "{exp_name}",
        "arm_index": selection["arm_index"],
        "reward": 1.0  # 1.0 for conversion, 0.0 for no conversion
    }}
)
                        """, language="python")
                
                except Exception as e:
                    st.error(f"Error creating experiment: {str(e)}")

# Tab 3: Manage Experiments
with tab3:
    st.header("Manage Experiments")
    
    try:
        experiments = api_client.list_experiments()
        
        if not experiments:
            st.info("No experiments to manage")
        else:
            st.warning("⚠️ Deleting an experiment cannot be undone!")
            
            exp_to_delete = st.selectbox(
                "Select Experiment to Delete",
                options=[exp['name'] for exp in experiments],
                format_func=lambda x: f"{x} ({next(e['algorithm'] for e in experiments if e['name']==x)})"
            )
            
            if exp_to_delete:
                # Show experiment details
                exp_data = next(e for e in experiments if e['name'] == exp_to_delete)
                
                st.write("**Experiment Details:**")
                st.json(exp_data)
                
                # Confirmation
                confirm = st.checkbox(f"I confirm I want to delete '{exp_to_delete}'")
                
                if st.button("🗑️ Delete Experiment", disabled=not confirm, type="primary"):
                    try:
                        api_client.delete_experiment(exp_to_delete)
                        st.success(f"Experiment '{exp_to_delete}' deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting experiment: {str(e)}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")