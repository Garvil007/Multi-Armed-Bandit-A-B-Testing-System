import requests
from typing import List, Dict, Optional
import streamlit as st

class MABAPIClient:
    """Client for interacting with MAB API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def create_experiment(
        self,
        name: str,
        arms: List[str],
        algorithm: str,
        epsilon: float = 0.1,
        c: float = 2.0
    ) -> Dict:
        """Create new experiment"""
        payload = {
            "experiment_name": name,
            "arms": arms,
            "algorithm": algorithm,
            "epsilon": epsilon,
            "c": c
        }
        response = self.session.post(
            f"{self.base_url}/experiments",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def list_experiments(self) -> List[Dict]:
        """List all experiments"""
        response = self.session.get(f"{self.base_url}/experiments")
        response.raise_for_status()
        return response.json()["experiments"]
    
    def get_experiment_stats(self, name: str) -> Dict:
        """Get experiment statistics"""
        response = self.session.get(
            f"{self.base_url}/experiments/{name}/stats"
        )
        response.raise_for_status()
        return response.json()
    
    def select_arm(self, experiment_name: str, user_id: Optional[str] = None) -> Dict:
        """Select arm for user"""
        payload = {
            "experiment_name": experiment_name,
            "user_id": user_id
        }
        response = self.session.post(
            f"{self.base_url}/select",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def update_reward(
        self,
        experiment_name: str,
        arm_index: int,
        reward: float,
        user_id: Optional[str] = None
    ) -> Dict:
        """Update reward for arm"""
        payload = {
            "experiment_name": experiment_name,
            "arm_index": arm_index,
            "reward": reward,
            "user_id": user_id
        }
        response = self.session.post(
            f"{self.base_url}/update",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def delete_experiment(self, name: str) -> Dict:
        """Delete experiment"""
        response = self.session.delete(
            f"{self.base_url}/experiments/{name}"
        )
        response.raise_for_status()
        return response.json()

@st.cache_resource
def get_api_client(base_url: str) -> MABAPIClient:
    """Get cached API client instance"""
    return MABAPIClient(base_url)