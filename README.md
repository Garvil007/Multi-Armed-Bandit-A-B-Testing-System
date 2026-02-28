# Multi-Armed Bandit A/B Testing Platform

Complete MLOps platform for dynamic A/B testing using Multi-Armed Bandit algorithms with interactive Streamlit dashboard.

## 🎯 Features

### Core Capabilities
- **3 MAB Algorithms**: Epsilon-Greedy, Thompson Sampling, UCB
- **REST API**: FastAPI-based microservice
- **Interactive Dashboard**: Real-time Streamlit interface
- **Experiment Tracking**: MLflow integration
- **Monitoring**: Prometheus + Grafana
- **Containerized**: Full Docker Compose stack

### Dashboard Features
- 🏠 Overview with quick stats
- 🧪 Experiment creation and management
- 📊 Real-time analytics and visualizations
- 🎯 Interactive simulation with custom scenarios
- ⚙️ Configuration and settings

## 🚀 Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone repository
git clone <your-repo>
cd mab-ab-testing

# Start all services
docker-compose up -d

# Access applications
# Streamlit: http://localhost:8501
# API Docs: http://localhost:8000/docs
# Grafana: http://localhost:3000
```

### Local Development
```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.app:app --reload

# Frontend (new terminal)
streamlit run streamlit_app/app.py
```

## 📊 Using the Dashboard

### 1. Create Experiment
- Navigate to 🧪 Experiments tab
- Click "Create New"
- Configure arms and algorithm
- Launch experiment

### 2. Run Simulations
- Go to 🎯 Simulate tab
- Select experiment
- Configure true conversion rates
- Run simulations and analyze

### 3. Monitor Performance
- View 📊 Analytics for real-time metrics
- Track convergence and regret
- Export data for analysis

## 🏗️ Architecture
```
┌─────────────────┐
│   Streamlit     │  ← User Interface
│   Dashboard     │
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│   FastAPI       │  ← Business Logic
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
┌───▼───┐ ┌──▼──┐ ┌────▼────┐ ┌──▼──────┐
│MLflow │ │Prom │ │ Models  │ │ Grafana │
└───────┘ └─────┘ └─────────┘ └─────────┘
```

## 📁 Project Structure
```
mab-ab-testing/
├── src/
│   ├── agents/          # MAB algorithms
│   ├── api/             # FastAPI application
│   └── monitoring/      # MLflow tracking
├── streamlit_app/       # Streamlit dashboard
│   ├── pages/          # Dashboard pages
│   ├── utils/          # Helper utilities
│   └── config.py       # Configuration
├── tests/              # Test suite
├── docker/             # Docker configurations
├── config/             # Monitoring configs
└── notebooks/          # Analysis notebooks
```

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html

# Test deployment
pytest tests/test_streamlit.py -v
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](DEPLOYMENT.md)
- [Launch Checklist](LAUNCH_CHECKLIST.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🎓 Learning Resources

- [Sutton & Barto - RL Book](http://incompleteideas.net/book/the-book.html)
- [Bandit Algorithms](https://tor-lattimore.com/downloads/book/book.pdf)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Streamlit Docs](https://docs.streamlit.io/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests
5. Submit pull request

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

Built for learning Reinforcement Learning and MLOps best practices.

---

**Ready to optimize your A/B tests? Start the dashboard and create your first experiment!** 🚀