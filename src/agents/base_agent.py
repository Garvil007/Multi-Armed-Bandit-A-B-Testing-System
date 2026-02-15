from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict
import json
from datetime import datetime

class BaseAgent(ABC):
    """Base class for Multi-Armed Bandit agents"""
    
    def __init__(self, n_arms: int, arm_names: List[str] = None):
        self.n_arms = n_arms
        self.arm_names = arm_names or [f"Arm_{i}" for i in range(n_arms)]
        self.counts = np.zeros(n_arms)  # Number of times each arm pulled
        self.values = np.zeros(n_arms)  # Average reward for each arm
        self.total_reward = 0
        self.total_pulls = 0
        
    @abstractmethod
    def select_arm(self) -> int:
        """Select which arm to pull"""
        pass
    
    def update(self, arm: int, reward: float):
        """Update agent after pulling arm and receiving reward"""
        self.counts[arm] += 1
        self.total_pulls += 1
        self.total_reward += reward
        
        # Incremental average update
        n = self.counts[arm]
        value = self.values[arm]
        self.values[arm] = ((n - 1) / n) * value + (1 / n) * reward
    
    def get_stats(self) -> Dict:
        """Return current statistics"""
        return {
            "total_pulls": int(self.total_pulls),
            "total_reward": float(self.total_reward),
            "average_reward": float(self.total_reward / max(self.total_pulls, 1)),
            "arm_counts": self.counts.tolist(),
            "arm_values": self.values.tolist(),
            "arm_names": self.arm_names
        }
    
    def save_state(self, filepath: str):
        """Save agent state to file"""
        state = {
            "n_arms": self.n_arms,
            "arm_names": self.arm_names,
            "counts": self.counts.tolist(),
            "values": self.values.tolist(),
            "total_reward": self.total_reward,
            "total_pulls": self.total_pulls,
            "timestamp": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load agent state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.counts = np.array(state["counts"])
        self.values = np.array(state["values"])
        self.total_reward = state["total_reward"]
        self.total_pulls = state["total_pulls"]