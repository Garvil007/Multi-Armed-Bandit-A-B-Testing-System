import pytest
import numpy as np
from src.agents import EpsilonGreedy, ThompsonSampling, UCB

@pytest.fixture
def n_arms():
    return 3

@pytest.fixture
def arm_names():
    return ["Ad_A", "Ad_B", "Ad_C"]

class TestEpsilonGreedy:
    def test_initialization(self, n_arms, arm_names):
        agent = EpsilonGreedy(n_arms, epsilon=0.1, arm_names=arm_names)
        assert agent.n_arms == n_arms
        assert len(agent.counts) == n_arms
        assert len(agent.values) == n_arms
        assert agent.epsilon == 0.1
    
    def test_select_arm(self, n_arms):
        agent = EpsilonGreedy(n_arms, epsilon=0.1)
        arm = agent.select_arm()
        assert 0 <= arm < n_arms
    
    def test_update(self, n_arms):
        agent = EpsilonGreedy(n_arms)
        agent.update(0, 1.0)
        assert agent.counts[0] == 1
        assert agent.values[0] == 1.0
        assert agent.total_reward == 1.0
    
    def test_exploitation(self, n_arms):
        """Test that agent exploits best arm when epsilon=0"""
        agent = EpsilonGreedy(n_arms, epsilon=0.0)
        # Give arm 1 higher reward
        for _ in range(10):
            agent.update(1, 1.0)
        
        # Should always select arm 1
        selections = [agent.select_arm() for _ in range(100)]
        assert all(arm == 1 for arm in selections)

class TestThompsonSampling:
    def test_initialization(self, n_arms, arm_names):
        agent = ThompsonSampling(n_arms, arm_names=arm_names)
        assert len(agent.alpha) == n_arms
        assert len(agent.beta) == n_arms
        assert all(agent.alpha == 1.0)
        assert all(agent.beta == 1.0)
    
    def test_beta_update_success(self, n_arms):
        agent = ThompsonSampling(n_arms)
        initial_alpha = agent.alpha[0]
        agent.update(0, 1.0)  # Success
        assert agent.alpha[0] == initial_alpha + 1
    
    def test_beta_update_failure(self, n_arms):
        agent = ThompsonSampling(n_arms)
        initial_beta = agent.beta[0]
        agent.update(0, 0.0)  # Failure
        assert agent.beta[0] == initial_beta + 1

class TestUCB:
    def test_initialization(self, n_arms):
        agent = UCB(n_arms, c=2.0)
        assert agent.c == 2.0
    
    def test_initial_exploration(self, n_arms):
        """Test that UCB pulls each arm once initially"""
        agent = UCB(n_arms)
        arms_selected = [agent.select_arm() for _ in range(n_arms)]
        assert set(arms_selected) == set(range(n_arms))

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])