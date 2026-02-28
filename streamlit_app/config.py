import os
from typing import Dict

class Config:
    """Application configuration"""
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # Streamlit Configuration
    PAGE_TITLE = "MAB A/B Testing Platform"
    PAGE_ICON = "🎰"
    LAYOUT = "wide"
    
    # Refresh intervals (seconds)
    METRICS_REFRESH_INTERVAL = 5
    STATS_REFRESH_INTERVAL = 10
    
    # Visualization settings
    PLOTLY_THEME = "plotly_white"
    COLOR_PALETTE = {
        "primary": "#1f77b4",
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "danger": "#d62728",
        "info": "#17becf"
    }
    
    # Algorithm descriptions
    ALGORITHM_INFO: Dict[str, str] = {
        "epsilon_greedy": """
        **Epsilon-Greedy**: Simple exploration-exploitation strategy.
        - Explores random arm with probability ε
        - Exploits best arm with probability (1-ε)
        - Good for: Quick convergence, stable environments
        """,
        "thompson_sampling": """
        **Thompson Sampling**: Bayesian approach using Beta distributions.
        - Samples from posterior distributions
        - Naturally balances exploration/exploitation
        - Good for: Binary rewards, delayed feedback
        """,
        "ucb": """
        **Upper Confidence Bound**: Optimistic approach.
        - Selects arm with highest upper confidence bound
        - Systematic exploration of uncertain arms
        - Good for: Theoretical guarantees, deterministic behavior
        """
    }
    
    # Simulation presets
    SIMULATION_PRESETS = {
        "Quick Test": {"iterations": 100, "speed": "fast"},
        "Standard": {"iterations": 500, "speed": "medium"},
        "Comprehensive": {"iterations": 1000, "speed": "slow"},
        "Production": {"iterations": 5000, "speed": "batch"}
    }

config = Config()