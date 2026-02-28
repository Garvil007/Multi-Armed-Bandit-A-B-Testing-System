import streamlit as st
import numpy as np
from typing import List, Dict
import time

def simulate_user_behavior(true_rates: List[float], arm_index: int) -> float:
    """Simulate user conversion based on true rates"""
    conversion_rate = true_rates[arm_index]
    return 1.0 if np.random.random() < conversion_rate else 0.0

def calculate_optimal_reward(true_rates: List[float], n_iterations: int) -> float:
    """Calculate optimal cumulative reward"""
    return max(true_rates) * n_iterations

def calculate_regret(cumulative_reward: float, optimal_reward: float) -> float:
    """Calculate cumulative regret"""
    return optimal_reward - cumulative_reward

def format_number(num: float, precision: int = 2) -> str:
    """Format number with appropriate suffix"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.{precision}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"

def show_success_message(message: str, duration: int = 3):
    """Show temporary success message"""
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(duration)
    placeholder.empty()

def show_error_message(message: str, duration: int = 5):
    """Show temporary error message"""
    placeholder = st.empty()
    placeholder.error(message)
    time.sleep(duration)
    placeholder.empty()

def validate_experiment_name(name: str) -> bool:
    """Validate experiment name"""
    if not name:
        return False
    if len(name) < 3:
        return False
    if not name.replace('_', '').replace('-', '').isalnum():
        return False
    return True

def get_algorithm_emoji(algorithm: str) -> str:
    """Get emoji for algorithm type"""
    emojis = {
        "epsilon_greedy": "🎲",
        "thompson_sampling": "🔬",
        "ucb": "📈"
    }
    return emojis.get(algorithm, "🤖")

class SessionState:
    """Manage session state"""
    
    @staticmethod
    def initialize():
        """Initialize session state variables"""
        defaults = {
            'simulation_running': False,
            'simulation_history': [],
            'current_experiment': None,
            'api_connected': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get(key: str, default=None):
        """Get session state value"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value):
        """Set session state value"""
        st.session_state[key] = value