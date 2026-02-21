import numpy as np
from .base_agent import BaseAgent

class UCB(BaseAgent):
    """Upper Confidence Bound MAB Algorithm"""
    
    def __init__(self, n_arms: int, c: float = 2.0, arm_names: list = None):
        super().__init__(n_arms, arm_names)
        self.c = c  # Exploration parameter
        self.algorithm_name = "ucb"
        self._pending = set()  # arms selected but not yet updated (initial exploration)
    
    def select_arm(self) -> int:
        """
        Select arm using UCB formula:
        UCB = mean_reward + c * sqrt(ln(total_pulls) / arm_pulls)

        During initial exploration every arm is pulled once.
        _pending tracks arms that have been selected but whose counts
        haven't been updated yet, so back-to-back select_arm() calls
        (without interleaved update()) still explore all arms.
        """
        for arm in range(self.n_arms):
            if self.counts[arm] == 0 and arm not in self._pending:
                self._pending.add(arm)
                return arm

        # All arms visited — apply UCB formula
        safe_counts = np.maximum(self.counts, 1e-5)
        ucb_values = self.values + self.c * np.sqrt(
            np.log(max(self.total_pulls, 1)) / safe_counts
        )
        return int(np.argmax(ucb_values))

    def update(self, arm: int, reward: float):
        """Update reward and remove arm from pending set."""
        self._pending.discard(arm)
        super().update(arm, reward)
    
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