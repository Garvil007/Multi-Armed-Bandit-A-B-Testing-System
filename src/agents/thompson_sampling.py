import numpy as np
from .base_agent import BaseAgent

class ThompsonSampling(BaseAgent):
    """Thompson Sampling MAB Algorithm (Beta-Bernoulli)"""
    
    def __init__(self, n_arms: int, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        # Beta distribution parameters (successes, failures)
        self.alpha = np.ones(n_arms)  # Prior: alpha = 1
        self.beta = np.ones(n_arms)   # Prior: beta = 1
        self.algorithm_name = "Thompson Sampling"
    
    def select_arm(self) -> int:
        """
        Sample from Beta distribution for each arm
        and select the arm with highest sample
        """
        samples = np.random.beta(self.alpha, self.beta)
        return np.argmax(samples)
    
    def update(self, arm: int, reward: float):
        """
        Update Beta parameters based on reward
        Assumes binary rewards (0 or 1)
        """
        super().update(arm, reward)
        
        # Update Beta distribution parameters
        if reward > 0.5:  # Success
            self.alpha[arm] += 1
        else:  # Failure
            self.beta[arm] += 1
    
    def get_stats(self) -> dict:
        """Extended stats with Beta parameters"""
        stats = super().get_stats()
        stats["alpha"] = self.alpha.tolist()
        stats["beta"] = self.beta.tolist()
        stats["algorithm"] = self.algorithm_name
        return stats
    
    def save_state(self, filepath: str):
        """Extended save with Beta parameters"""
        import json
        from datetime import datetime
        
        state = {
            "n_arms": self.n_arms,
            "arm_names": self.arm_names,
            "counts": self.counts.tolist(),
            "values": self.values.tolist(),
            "alpha": self.alpha.tolist(),
            "beta": self.beta.tolist(),
            "total_reward": self.total_reward,
            "total_pulls": self.total_pulls,
            "timestamp": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Extended load with Beta parameters"""
        import json
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        super().load_state(filepath)
        self.alpha = np.array(state["alpha"])
        self.beta = np.array(state["beta"])