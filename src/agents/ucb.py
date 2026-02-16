import numpy as np
from .base_agent import BaseAgent

class UCB(BaseAgent):
    """Upper Confidence Bound MAB Algorithm"""
    
    def __init__(self, n_arms: int, c: float = 2.0, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        self.c = c  # Exploration parameter
        self.algorithm_name = "ucb"
    
    def select_arm(self) -> int:
        """
        Select arm using UCB formula:
        UCB = mean_reward + c * sqrt(ln(total_pulls) / arm_pulls)
        """
        # Pull each arm once initially
        for arm in range(self.n_arms):
            if self.counts[arm] == 0:
                return arm
        
        # Calculate UCB for each arm
        # Avoid division by zero (though handled by initial pull check)
        # Using 1e-5 to prevent runtime warning if counts somehow 0
        safe_counts = np.maximum(self.counts, 1e-5)
        
        ucb_values = self.values + self.c * np.sqrt(
            np.log(self.total_pulls) / safe_counts
        )
        
        return np.argmax(ucb_values)
    
    def get_stats(self) -> dict:
        """Extended stats with c parameter"""
        stats = super().get_stats()
        stats["c"] = self.c
        stats["algorithm"] = self.algorithm_name
        return stats
        
    def save_state(self, filepath: str):
        """Save state including c parameter"""
        super().save_state(filepath, c=self.c)
        
    def load_state(self, filepath: str):
        """Load state including c parameter"""
        state = super().load_state(filepath)
        self.c = state.get("c", 2.0)