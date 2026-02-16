from typing import Dict, Optional
import os
import json
from datetime import datetime
from src.agents import EpsilonGreedy, ThompsonSampling, UCB
from .models import AlgorithmType

class ExperimentManager:
    """Manages multiple MAB experiments"""
    
    def __init__(self, storage_dir: str = "models"):
        self.experiments: Dict = {}
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def create_experiment(
        self, 
        name: str, 
        arms: list, 
        algorithm: AlgorithmType,
        epsilon: float = 0.1,
        c: float = 2.0
    ):
        """Create new experiment"""
        if name in self.experiments:
            raise ValueError(f"Experiment '{name}' already exists")
        
        n_arms = len(arms)
        
        # Initialize appropriate agent
        if algorithm == AlgorithmType.EPSILON_GREEDY:
            agent = EpsilonGreedy(n_arms, epsilon, arms)
        elif algorithm == AlgorithmType.THOMPSON_SAMPLING:
            agent = ThompsonSampling(n_arms, arms)
        elif algorithm == AlgorithmType.UCB:
            agent = UCB(n_arms, c, arms)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        self.experiments[name] = {
            "agent": agent,
            "created_at": datetime.now().isoformat(),
            "algorithm": algorithm.value
        }
        
        # Save initial state
        self._save_experiment(name)
        
        return {"message": f"Experiment '{name}' created successfully"}
    
    def get_experiment(self, name: str):
        """Get experiment agent"""
        if name not in self.experiments:
            raise ValueError(f"Experiment '{name}' not found")
        return self.experiments[name]["agent"]
    
    def select_arm(self, name: str) -> tuple:
        """Select arm for experiment"""
        agent = self.get_experiment(name)
        arm_index = agent.select_arm()
        arm_name = agent.arm_names[arm_index]
        return arm_index, arm_name
    
    def update_reward(self, name: str, arm: int, reward: float):
        """Update reward for selected arm"""
        agent = self.get_experiment(name)
        agent.update(arm, reward)
        self._save_experiment(name)
    
    def get_stats(self, name: str) -> dict:
        """Get experiment statistics"""
        agent = self.get_experiment(name)
        stats = agent.get_stats()
        stats["experiment_name"] = name
        return stats
    
    def list_experiments(self) -> list:
        """List all experiments"""
        return [
            {
                "name": name,
                "algorithm": exp["algorithm"],
                "created_at": exp["created_at"],
                "total_pulls": exp["agent"].total_pulls
            }
            for name, exp in self.experiments.items()
        ]
    
    def _save_experiment(self, name: str):
        """Save experiment state to disk"""
        filepath = os.path.join(self.storage_dir, f"{name}.json")
        agent = self.experiments[name]["agent"]
        agent.save_state(filepath)
    
    def load_all_experiments(self):
        """Load all experiments from disk on startup"""
        if not os.path.exists(self.storage_dir):
            return 0
            
        loaded_count = 0
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith('.json'):
                continue
                
            experiment_name = filename[:-5]  # Remove .json
            filepath = os.path.join(self.storage_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    state = json.load(f)
                
                # Extract metadata for initialization
                algo_type = state.get("algorithm")
                n_arms = state.get("n_arms")
                arm_names = state.get("arm_names")
                
                if not algo_type or not n_arms:
                    print(f"Skipping invalid experiment file: {filename}")
                    continue
                
                # Initialize appropriate agent
                agent = None
                if algo_type == AlgorithmType.EPSILON_GREEDY.value:
                    epsilon = state.get("epsilon", 0.1)
                    agent = EpsilonGreedy(n_arms, epsilon=epsilon, arm_names=arm_names)
                elif algo_type == AlgorithmType.THOMPSON_SAMPLING.value:
                    agent = ThompsonSampling(n_arms, arm_names=arm_names)
                elif algo_type == AlgorithmType.UCB.value:
                    c = state.get("c", 2.0)
                    agent = UCB(n_arms, c=c, arm_names=arm_names)
                
                if agent:
                    # Restore full state (counts, values, etc.)
                    agent.load_state(filepath)
                    
                    self.experiments[experiment_name] = {
                        "agent": agent,
                        "created_at": state.get("timestamp", datetime.now().isoformat()),
                        "algorithm": algo_type
                    }
                    loaded_count += 1
                    
            except Exception as e:
                print(f"Failed to load experiment {filename}: {e}")
                
        return loaded_count