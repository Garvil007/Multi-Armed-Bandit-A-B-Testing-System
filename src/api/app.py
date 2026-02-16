from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from .models import (
    CreateExperimentRequest, 
    SelectArmRequest, 
    UpdateRewardRequest,
    ArmSelection,
    ExperimentStats
)
from .experiment_manager import ExperimentManager
from .metrics import metrics, track_arm_selection, track_reward

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Armed Bandit A/B Testing API",
    description="Production-ready MAB system for dynamic content optimization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize experiment manager
manager = ExperimentManager()

@app.get("/")
def read_root():
    return {
        "message": "Multi-Armed Bandit A/B Testing API",
        "version": "1.0.0",
        "endpoints": {
            "create": "/experiments",
            "select": "/select",
            "update": "/update",
            "stats": "/experiments/{name}/stats",
            "list": "/experiments",
            "metrics": "/metrics"
        }
    }

@app.post("/experiments", status_code=201)
def create_experiment(request: CreateExperimentRequest):
    """Create a new MAB experiment"""
    try:
        result = manager.create_experiment(
            name=request.experiment_name,
            arms=request.arms,
            algorithm=request.algorithm,
            epsilon=request.epsilon,
            c=request.c
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/select", response_model=ArmSelection)
def select_arm(request: SelectArmRequest):
    """Select an arm for the user"""
    try:
        arm_index, arm_name = manager.select_arm(request.experiment_name)
        
        # Track metrics
        track_arm_selection(request.experiment_name, arm_name)
        
        return ArmSelection(
            experiment_name=request.experiment_name,
            arm_index=arm_index,
            arm_name=arm_name,
            timestamp=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/update")
def update_reward(request: UpdateRewardRequest):
    """Update reward for a selected arm"""
    try:
        manager.update_reward(
            request.experiment_name,
            request.arm_index,
            request.reward
        )
        
        # Track metrics
        track_reward(request.experiment_name, request.reward)
        
        return {"message": "Reward updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/experiments/{name}/stats", response_model=ExperimentStats)
def get_experiment_stats(name: str):
    """Get statistics for an experiment"""
    try:
        stats = manager.get_stats(name)
        return ExperimentStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/experiments")
def list_experiments():
    """List all experiments"""
    return {"experiments": manager.list_experiments()}

@app.delete("/experiments/{name}")
def delete_experiment(name: str):
    """Delete an experiment"""
    try:
        if name in manager.experiments:
            del manager.experiments[name]
            return {"message": f"Experiment '{name}' deleted"}
        else:
            raise ValueError(f"Experiment '{name}' not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)