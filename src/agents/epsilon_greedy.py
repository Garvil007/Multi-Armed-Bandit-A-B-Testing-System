import numpy as np
from .base_agent import BaseAgent

class EpsilonGreedy(BaseAgent):
    """Epsilon-Greedy MAB Algorithm"""
    
    def __init__(self, n_arms: int, epsilon: float = 0.1, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        self.epsilon = epsilon
        self.algorithm_name = "epsilon_greedy"
    
    def select_arm(self) -> int:
        """
        Select arm using epsilon-greedy strategy:
        - With probability epsilon: explore (random arm)
        - With probability 1-epsilon: exploit (best arm)
        """
        if np.random.random() < self.epsilon:
            # Explore: random selection
            return np.random.randint(0, self.n_arms)
        else:
            # Exploit: choose best arm (break ties randomly)
            max_value = np.max(self.values)
            best_arms = np.where(self.values == max_value)[0]
            return np.random.choice(best_arms)
    
    def get_stats(self) -> dict:
        """Extended stats with epsilon value"""
        stats = super().get_stats()
        stats["epsilon"] = self.epsilon
        stats["algorithm"] = self.algorithm_name
        return stats
        
    def save_state(self, filepath: str):
        """Save state including epsilon"""
        super().save_state(filepath, epsilon=self.epsilon)
        
    def load_state(self, filepath: str):
        """Load state including epsilon"""
        state = super().load_state(filepath)
        self.epsilon = state.get("epsilon", 0.1)