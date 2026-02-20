from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Define metrics
arm_selections = Counter(
    'mab_arm_selections_total',
    'Total number of arm selections',
    ['experiment', 'arm']
)

rewards_total = Counter(
    'mab_rewards_total',
    'Total rewards received',
    ['experiment']
)

reward_distribution = Histogram(
    'mab_reward_value',
    'Distribution of reward values',
    ['experiment'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

active_experiments = Gauge(
    'mab_active_experiments',
    'Number of active experiments'
)

def track_arm_selection(experiment: str, arm: str):
    """Track arm selection"""
    arm_selections.labels(experiment=experiment, arm=arm).inc()

def track_reward(experiment: str, reward: float):
    """Track reward"""
    rewards_total.labels(experiment=experiment).inc()
    reward_distribution.labels(experiment=experiment).observe(reward)