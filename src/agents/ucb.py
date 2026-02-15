import numpy as np
from .base_agent import BaseAgent

class UCB(BaseAgent):
    """Upper Confidence Bound MAB Algorithm"""
    
    def __init__(self, n_arms: int, c: float = 2.0, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        self.c = c  # Exploration parameter
        self.algorithm_name = "UCB"
    
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
        ucb_values = self.values + self.c * np.sqrt(
            np.log(self.total_pulls) / self.counts
        )
        
        return np.argmax(ucb_values)
    
    def get_stats(self) -> dict:
        """Extended stats with c parameter"""
        stats = super().get_stats()
        stats["c"] = self.c
        stats["algorithm"] = self.algorithm_name
        return stats