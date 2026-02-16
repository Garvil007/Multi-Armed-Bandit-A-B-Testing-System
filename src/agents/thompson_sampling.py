import numpy as np
import json
from datetime import datetime
from .base_agent import BaseAgent

class ThompsonSampling(BaseAgent):
    """Thompson Sampling MAB Algorithm (Beta-Bernoulli)"""
    
    def __init__(self, n_arms: int, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        # Beta distribution parameters (successes, failures)
        self.alpha = np.ones(n_arms)  # Prior: alpha = 1
        self.beta = np.ones(n_arms)   # Prior: beta = 1
        self.algorithm_name = "thompson_sampling"
    
    def select_arm(self) -> int:
        """
        Sample from Beta distribution for each arm
        and select the arm with highest sample
        """
        # Ensure alpha/beta are > 0
        safe_alpha = np.maximum(self.alpha, 1e-5)
        safe_beta = np.maximum(self.beta, 1e-5)
        
        samples = np.random.beta(safe_alpha, safe_beta)
        return np.argmax(samples)
    
    def update(self, arm: int, reward: float):
        """
        Update Beta parameters based on reward
        Assumes binary rewards (0 or 1)
        """
        super().update(arm, reward)
        
        # Update Beta distribution parameters
        # Probabilistic update for non-binary rewards if needed
        # But standard TS assumes binary Bernoulli.
        # If reward is continuous [0,1], we can use Bernoulli trial
        if reward > np.random.random():  # Probabilistic update for [0,1] rewards
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1
            
        # Or strict binary if reward is exactly 0 or 1
        # if reward > 0.5: self.alpha[arm] += 1 ...
    
    def get_stats(self) -> dict:
        """Extended stats with Beta parameters"""
        stats = super().get_stats()
        stats["alpha"] = self.alpha.tolist()
        stats["beta"] = self.beta.tolist()
        stats["algorithm"] = self.algorithm_name
        return stats
    
    def save_state(self, filepath: str):
        """Extended save with Beta parameters"""
        # Reuse super save_state with kwargs
        super().save_state(filepath, alpha=self.alpha.tolist(), beta=self.beta.tolist())
    
    def load_state(self, filepath: str):
        """Extended load with Beta parameters"""
        state = super().load_state(filepath)
        self.alpha = np.array(state.get("alpha", np.ones(self.n_arms)))
        self.beta = np.array(state.get("beta", np.ones(self.n_arms)))