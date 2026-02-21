# Multi-Armed Bandit A/B Testing System

Production-ready dynamic content recommendation system using Multi-Armed Bandit algorithms with full MLOps pipeline.

## Features

- **3 MAB Algorithms**: Epsilon-Greedy, Thompson Sampling, UCB
- **REST API**: FastAPI-based service
- **Experiment Tracking**: MLflow integration
- **Monitoring**: Prometheus + Grafana dashboards
- **Containerized**: Docker & Docker Compose
- **CI/CD**: GitHub Actions pipeline
- **Testing**: Pytest with >90% coverage

## Quick Start

### Local Development
```bash
# Clone repository
git clone <your-repo-url>
cd mab-ab-testing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API
uvicorn src.api.app:app --reload

# Access API docs
open http://localhost:8000/docs
```

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# Access services
# API: http://localhost:8000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

## API Usage

### Create Experiment
```bash
curl -X POST http://localhost:8000/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "homepage_banner",
    "arms": ["Banner_A", "Banner_B", "Banner_C"],
    "algorithm": "thompson_sampling"
  }'
```

### Select Arm
```bash
curl -X POST http://localhost:8000/select \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "homepage_banner",
    "user_id": "user123"
  }'
```

### Update Reward
```bash
curl -X POST http://localhost:8000/update \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "homepage_banner",
    "arm_index": 0,
    "reward": 1.0
  }'
```

### Get Statistics
```bash
curl http://localhost:8000/experiments/homepage_banner/stats
```

## Project Structure
```
mab-ab-testing/
├── src/
│   ├── agents/           # MAB algorithms
│   ├── api/              # FastAPI application
│   └── monitoring/       # MLflow tracking
├── tests/                # Unit tests
├── notebooks/            # Jupyter notebooks
├── docker/               # Docker configuration
├── config/               # Prometheus & Grafana config
└── models/               # Saved agent states
```

## Monitoring

- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000
- **MLflow UI**: `mlflow ui` (http://localhost:5000)

## Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License