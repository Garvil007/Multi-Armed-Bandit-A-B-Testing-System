import streamlit as st
import numpy as np
import time
from datetime import datetime
from utils.api_client import get_api_client
from utils.visualizations import (
    create_reward_timeline,
    create_arm_evolution,
    create_regret_plot,
    create_arm_comparison
)
from utils.helpers import (
    SessionState,
    simulate_user_behavior,
    calculate_optimal_reward,
    format_number
)
from config import config
import pandas as pd

st.set_page_config(
    page_title="Simulate - MAB Platform",
    page_icon="🎯",
    layout="wide"
)

# Initialize
SessionState.initialize()
api_client = get_api_client(config.API_BASE_URL)

st.title("🎯 Experiment Simulation")
st.markdown("Test your MAB experiments with synthetic data and customizable scenarios")

# Check API connection
if not api_client.health_check():
    st.error("❌ Cannot connect to API")
    st.stop()

# Get experiments
try:
    experiments = api_client.list_experiments()
    
    if not experiments:
        st.warning("No experiments available. Create one first!")
        if st.button("➕ Create Experiment"):
            st.switch_page("pages/2_🧪_Experiments.py")
        st.stop()
    
    # Experiment selector
    current_exp = SessionState.get('current_experiment')
    if current_exp not in [e['name'] for e in experiments]:
        current_exp = experiments[0]['name']
    
    selected_exp = st.selectbox(
        "Select Experiment to Simulate",
        options=[e['name'] for e in experiments],
        index=[e['name'] for e in experiments].index(current_exp)
    )
    
    SessionState.set('current_experiment', selected_exp)
    
    # Get experiment details
    stats = api_client.get_experiment_stats(selected_exp)
    n_arms = len(stats['arm_names'])
    
    st.markdown("---")
    
    # Simulation Configuration
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Simulation Settings")
        
        # Scenario presets
        scenario = st.selectbox(
            "Scenario Preset",
            options=["Custom", "Equal Arms", "Clear Winner", "Close Competition", "Multi-Modal"],
            help="Pre-configured reward distributions"
        )
        
        # True conversion rates
        st.write("**True Conversion Rates** (ground truth):")
        
        true_rates = []
        
        if scenario == "Equal Arms":
            true_rates = [0.10] * n_arms
        elif scenario == "Clear Winner":
            true_rates = [0.05] * n_arms
            true_rates[0] = 0.20
        elif scenario == "Close Competition":
            base = 0.10
            true_rates = [base + i * 0.01 for i in range(n_arms)]
        elif scenario == "Multi-Modal":
            true_rates = [0.05, 0.15, 0.08] if n_arms >= 3 else [0.05, 0.15]
            true_rates.extend([0.10] * (n_arms - len(true_rates)))
        else:  # Custom
            for i, arm in enumerate(stats['arm_names']):
                rate = st.slider(
                    f"{arm}",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.05 + i * 0.03,
                    step=0.01,
                    key=f"rate_{i}"
                )
                true_rates.append(rate)
        
        # Display rates if not custom
        if scenario != "Custom":
            for i, arm in enumerate(stats['arm_names']):
                st.write(f"- {arm}: {true_rates[i]:.2%}")
        
        st.markdown("---")
        
        # Simulation parameters
        n_iterations = st.number_input(
            "Number of Iterations",
            min_value=10,
            max_value=10000,
            value=500,
            step=50,
            help="How many simulated interactions to run"
        )
        
        batch_size = st.selectbox(
            "Batch Size",
            options=[1, 10, 50, 100],
            index=1,
            help="Number of iterations per update (larger = faster)"
        )
        
        show_animation = st.checkbox(
            "Show Live Animation",
            value=True,
            help="Display real-time updates (slower)"
        )
        
        # Start simulation button
        st.markdown("---")
        
        if st.button("🚀 Start Simulation", type="primary", use_container_width=True):
            SessionState.set('simulation_running', True)
            SessionState.set('simulation_history', [])
        
        if st.button("🛑 Stop Simulation", use_container_width=True):
            SessionState.set('simulation_running', False)
        
        if st.button("🔄 Reset Experiment", use_container_width=True):
            if st.warning("This will reset all experiment data. Continue?"):
                # Note: You'd need to implement reset in the API
                st.info("Reset functionality - requires API endpoint")
    
    with col2:
        st.subheader("📊 Simulation Results")
        
        # Placeholder for real-time updates
        metrics_placeholder = st.empty()
        chart_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        # Run simulation
        if SessionState.get('simulation_running'):
            
            # Initialize tracking
            history = []
            cumulative_reward = 0
            optimal_reward = calculate_optimal_reward(true_rates, n_iterations)
            
            # Progress bar
            progress_bar = progress_placeholder.progress(0)
            status_text = st.empty()
            
            # Run iterations
            for iteration in range(1, n_iterations + 1):
                
                # Batch processing
                batch_rewards = []
                batch_arms = []
                
                for _ in range(min(batch_size, n_iterations - iteration + 1)):
                    # Select arm
                    selection = api_client.select_arm(selected_exp)
                    arm_index = selection['arm_index']
                    
                    # Simulate user behavior
                    reward = simulate_user_behavior(true_rates, arm_index)
                    
                    # Update reward
                    api_client.update_reward(selected_exp, arm_index, reward)
                    
                    batch_rewards.append(reward)
                    batch_arms.append(arm_index)
                    cumulative_reward += reward
                
                # Get updated stats
                current_stats = api_client.get_experiment_stats(selected_exp)
                
                # Record history
                history.append({
                    'iteration': iteration,
                    'cumulative_reward': cumulative_reward,
                    'average_reward': current_stats['average_reward'],
                    'arm_counts': current_stats['arm_counts'].copy(),
                    'arm_values': current_stats['arm_values'].copy(),
                    'regret': optimal_reward * (iteration / n_iterations) - cumulative_reward
                })
                
                # Update progress
                progress = iteration / n_iterations
                progress_bar.progress(progress)
                status_text.text(f"Iteration {iteration}/{n_iterations} - Avg Reward: {current_stats['average_reward']:.4f}")
                
                # Update visualizations (every N iterations or if animation enabled)
                if show_animation or iteration % max(1, n_iterations // 20) == 0 or iteration == n_iterations:
                    
                    # Metrics
                    with metrics_placeholder.container():
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Iterations", f"{iteration:,}")
                        with col2:
                            st.metric("Avg Reward", f"{current_stats['average_reward']:.4f}")
                        with col3:
                            regret = optimal_reward * (iteration / n_iterations) - cumulative_reward
                            st.metric("Regret", f"{regret:.2f}")
                        with col4:
                            best_arm_idx = current_stats['arm_values'].index(max(current_stats['arm_values']))
                            st.metric("Best Arm", stats['arm_names'][best_arm_idx])
                    
                    # Charts
                    with chart_placeholder.container():
                        tab1, tab2, tab3 = st.tabs(["📈 Rewards", "🎯 Arms", "📉 Regret"])
                        
                        with tab1:
                            if len(history) > 1:
                                fig = create_reward_timeline(history)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with tab2:
                            if len(history) > 1:
                                fig = create_arm_evolution(history, stats['arm_names'])
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with tab3:
                            if len(history) > 1:
                                fig = create_regret_plot(history, max(true_rates))
                                st.plotly_chart(fig, use_container_width=True)
                    
                    # Small delay for animation
                    if show_animation and batch_size == 1:
                        time.sleep(0.05)
            
            # Simulation complete
            SessionState.set('simulation_running', False)
            SessionState.set('simulation_history', history)
            
            progress_placeholder.empty()
            status_text.empty()
            
            st.success(f"✅ Simulation complete! Ran {n_iterations} iterations.")
            st.balloons()
            
            # Final comparison
            st.markdown("---")
            st.subheader("📊 Final Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Algorithm Performance:**")
                fig_final = create_arm_comparison(current_stats, true_rates)
                st.plotly_chart(fig_final, use_container_width=True)