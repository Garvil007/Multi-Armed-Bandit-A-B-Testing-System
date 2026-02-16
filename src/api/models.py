from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class AlgorithmType(str, Enum):
    EPSILON_GREEDY = "epsilon_greedy"
    THOMPSON_SAMPLING = "thompson_sampling"
    UCB = "ucb"

class CreateExperimentRequest(BaseModel):
    experiment_name: str = Field(..., description="Unique experiment name")
    arms: List[str] = Field(..., description="List of arm names (e.g., ad variants)")
    algorithm: AlgorithmType = Field(..., description="MAB algorithm to use")
    epsilon: Optional[float] = Field(0.1, description="Epsilon for epsilon-greedy")
    c: Optional[float] = Field(2.0, description="Exploration parameter for UCB")

class SelectArmRequest(BaseModel):
    experiment_name: str
    user_id: Optional[str] = None

class UpdateRewardRequest(BaseModel):
    experiment_name: str
    arm_index: int
    reward: float = Field(..., ge=0.0, le=1.0, description="Reward between 0 and 1")
    user_id: Optional[str] = None

class ArmSelection(BaseModel):
    experiment_name: str
    arm_index: int
    arm_name: str
    timestamp: str

class ExperimentStats(BaseModel):
    experiment_name: str
    algorithm: str
    total_pulls: int
    total_reward: float
    average_reward: float
    arm_counts: List[int]
    arm_values: List[float]
    arm_names: List[str]