import pytest
import requests
import time

class TestStreamlitDeployment:
    
    @pytest.fixture
    def api_url(self):
        return "http://localhost:8000"
    
    @pytest.fixture
    def streamlit_url(self):
        return "http://localhost:8501"
    
    def test_api_health(self, api_url):
        """Test API is running"""
        response = requests.get(f"{api_url}/health")
        assert response.status_code == 200
    
    def test_streamlit_health(self, streamlit_url):
        """Test Streamlit is running"""
        response = requests.get(f"{streamlit_url}/_stcore/health")
        assert response.status_code == 200
    
    def test_create_experiment_flow(self, api_url):
        """Test full experiment creation flow"""
        # Create experiment
        payload = {
            "experiment_name": "test_exp",
            "arms": ["A", "B", "C"],
            "algorithm": "epsilon_greedy",
            "epsilon": 0.1
        }
        
        response = requests.post(f"{api_url}/experiments", json=payload)
        assert response.status_code == 201
        
        # Select arm
        select_response = requests.post(
            f"{api_url}/select",
            json={"experiment_name": "test_exp"}
        )
        assert select_response.status_code == 200
        
        selection = select_response.json()
        
        # Update reward
        update_response = requests.post(
            f"{api_url}/update",
            json={
                "experiment_name": "test_exp",
                "arm_index": selection["arm_index"],
                "reward": 1.0
            }
        )
        assert update_response.status_code == 200
        
        # Get stats
        stats_response = requests.get(f"{api_url}/experiments/test_exp/stats")
        assert stats_response.status_code == 200
        
        # Cleanup
        requests.delete(f"{api_url}/experiments/test_exp")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])