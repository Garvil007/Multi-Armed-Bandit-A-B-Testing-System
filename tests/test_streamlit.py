import pytest
import requests

API_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"


def _is_service_up(url: str) -> bool:
    """Return True if the URL responds within 2 seconds."""
    try:
        requests.get(url, timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


# ── Markers ────────────────────────────────────────────────────────────────
# Run *only* integration tests:   pytest -m integration
# Skip  integration tests (CI):   pytest -m "not integration"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def api_available():
    """Skip all tests in this module if the API is not reachable."""
    if not _is_service_up(f"{API_URL}/health"):
        pytest.skip(
            "API server not running at localhost:8000 — skipping deployment tests. "
            "Start the API with `uvicorn src.api.app:app` before running these tests.",
            allow_module_level=True,
        )


@pytest.fixture(scope="session")
def streamlit_available():
    """Skip all tests in this module if Streamlit is not reachable."""
    if not _is_service_up(f"{STREAMLIT_URL}/_stcore/health"):
        pytest.skip(
            "Streamlit server not running at localhost:8501 — skipping deployment tests. "
            "Start Streamlit with `streamlit run streamlit_app/app.py` before running these tests.",
            allow_module_level=True,
        )


class TestStreamlitDeployment:

    def test_api_health(self, api_available):
        """Test API is running and healthy."""
        response = requests.get(f"{API_URL}/health", timeout=5)
        assert response.status_code == 200

    def test_streamlit_health(self, streamlit_available):
        """Test Streamlit is running and healthy."""
        response = requests.get(f"{STREAMLIT_URL}/_stcore/health", timeout=5)
        assert response.status_code == 200

    def test_create_experiment_flow(self, api_available):
        """Test full experiment lifecycle: create → select → update → stats → delete."""
        exp_name = "test_exp_ci"

        # Create
        response = requests.post(
            f"{API_URL}/experiments",
            json={
                "experiment_name": exp_name,
                "arms": ["A", "B", "C"],
                "algorithm": "epsilon_greedy",
                "epsilon": 0.1,
            },
            timeout=5,
        )
        assert response.status_code == 201, f"Create failed: {response.text}"

        # Select arm
        select_response = requests.post(
            f"{API_URL}/select",
            json={"experiment_name": exp_name},
            timeout=5,
        )
        assert select_response.status_code == 200, f"Select failed: {select_response.text}"
        arm_index = select_response.json()["arm_index"]

        # Update reward
        update_response = requests.post(
            f"{API_URL}/update",
            json={"experiment_name": exp_name, "arm_index": arm_index, "reward": 1.0},
            timeout=5,
        )
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"

        # Get stats
        stats_response = requests.get(f"{API_URL}/experiments/{exp_name}/stats", timeout=5)
        assert stats_response.status_code == 200, f"Stats failed: {stats_response.text}"

        # Cleanup
        requests.delete(f"{API_URL}/experiments/{exp_name}", timeout=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
