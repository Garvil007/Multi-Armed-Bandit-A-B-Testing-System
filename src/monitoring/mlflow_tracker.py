import mlflow
import mlflow.sklearn
from typing import Dict
import os

class MLflowTracker:
    """MLflow experiment tracking"""
    
    def __init__(self, tracking_uri: str = "./mlruns"):
        mlflow.set_tracking_uri(tracking_uri)
        self.experiment_name = "mab-ab-testing"
        mlflow.set_experiment(self.experiment_name)
    
    def start_run(self, run_name: str, tags: Dict = None):
        """Start new MLflow run"""
        return mlflow.start_run(run_name=run_name, tags=tags)
    
    def log_params(self, params: Dict):
        """Log parameters"""
        mlflow.log_params(params)
    
    def log_metrics(self, metrics: Dict, step: int = None):
        """Log metrics"""
        mlflow.log_metrics(metrics, step=step)
    
    def log_agent_state(self, agent, step: int):
        """Log complete agent state"""
        stats = agent.get_stats()
        
        # Log scalar metrics
        mlflow.log_metrics({
            "total_pulls": stats["total_pulls"],
            "total_reward": stats["total_reward"],
            "average_reward": stats["average_reward"]
        }, step=step)
        
        # Log per-arm metrics
        for i, (count, value) in enumerate(zip(stats["arm_counts"], stats["arm_values"])):
            mlflow.log_metrics({
                f"arm_{i}_pulls": count,
                f"arm_{i}_avg_reward": value
            }, step=step)
    
    def end_run(self):
        """End current run"""
        mlflow.end_run()

# Initialize global tracker
tracker = MLflowTracker()