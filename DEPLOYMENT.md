# Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- Ports 8000, 8501, 9090, 3000 available

### Steps

1. **Clone the repository**
```bash
git clone <your-repo>
cd mab-ab-testing
```

2. **Build and start all services**
```bash
docker-compose up -d
```

3. **Access the applications**
- Streamlit Dashboard: http://localhost:8501
- FastAPI Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

4. **Stop services**
```bash
docker-compose down
```

## Local Development Setup

### Backend (FastAPI)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API
uvicorn src.api.app:app --reload --port 8000
```

### Frontend (Streamlit)
```bash
# In the same virtual environment
streamlit run streamlit_app/app.py
```

### Monitoring
```bash
# Start MLflow
mlflow ui --host 0.0.0.0 --port 5000

# Prometheus and Grafana via Docker
docker-compose up prometheus grafana
```

## Production Deployment

### Option 1: AWS EC2

1. **Launch EC2 instance** (t2.medium or larger)
2. **Install Docker**
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

3. **Deploy application**
```bash
git clone <your-repo>
cd mab-ab-testing
docker-compose up -d
```

4. **Configure security groups**
- Port 8501 (Streamlit)
- Port 8000 (API)
- Port 3000 (Grafana)

### Option 2: Kubernetes

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mab-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mab-api
  template:
    metadata:
      labels:
        app: mab-api
    spec:
      containers:
      - name: api
        image: your-registry/mab-api:latest
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: mab-api-service
spec:
  selector:
    app: mab-api
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
```

### Option 3: Cloud Run (GCP)
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/mab-api

# Deploy
gcloud run deploy mab-api \
  --image gcr.io/PROJECT-ID/mab-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

Create `.env` file:
```bash
# API Configuration
API_BASE_URL=http://localhost:8000

# MLflow
MLFLOW_TRACKING_URI=./mlruns

# Monitoring
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Security
API_KEY=your-secret-key
```

## Monitoring Setup

### Grafana Dashboard Import

1. Open Grafana (http://localhost:3000)
2. Login (admin/admin)
3. Go to Dashboards → Import
4. Upload `config/grafana/dashboards/mab-dashboard.json`

### Alert Configuration

Add to `config/prometheus.yml`:
```yaml
alerting:
  alertmanagers:
  - static_configs:
    - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

Create `config/alerts.yml`:
```yaml
groups:
- name: mab_alerts
  rules:
  - alert: HighRewardDropoff
    expr: rate(mab_rewards_total[5m]) < 0.1
    for: 10m
    annotations:
      summary: "Reward rate has dropped significantly"
```

## Backup & Recovery

### Backup Experiment Data
```bash
# Backup models
tar -czf models-backup.tar.gz models/

# Backup MLflow runs
tar -czf mlruns-backup.tar.gz mlruns/
```

### Restore
```bash
tar -xzf models-backup.tar.gz
tar -xzf mlruns-backup.tar.gz
```

## Troubleshooting

### Common Issues

1. **API won't start**
   - Check if port 8000 is available
   - Verify Python version (3.10+)
   - Check logs: `docker logs mab-api`

2. **Streamlit connection error**
   - Ensure API is running
   - Check API_BASE_URL environment variable
   - Verify network connectivity

3. **Prometheus not scraping metrics**
   - Check Prometheus config
   - Verify `/metrics` endpoint is accessible
   - Check Prometheus logs

4. **Grafana dashboard not loading**
   - Verify Prometheus datasource is configured
   - Check Grafana logs
   - Ensure dashboard JSON is valid

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check Streamlit
curl http://localhost:8501/_stcore/health

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

## Security Considerations

1. **API Authentication**
   - Implement JWT tokens
   - Use API keys for production
   - Enable HTTPS/TLS

2. **Network Security**
   - Use VPC/private subnets
   - Configure firewall rules
   - Enable security groups

3. **Data Protection**
   - Encrypt sensitive data
   - Regular backups
   - Access control policies

## Performance Optimization

1. **API Scaling**
   - Use Gunicorn with multiple workers
   - Enable Redis caching
   - Implement connection pooling

2. **Database Optimization**
   - Add PostgreSQL for persistence
   - Index frequently queried fields
   - Implement query caching

3. **Monitoring**
   - Set up log aggregation (ELK stack)
   - Configure APM (Application Performance Monitoring)
   - Enable distributed tracing

## Cost Optimization

1. **Resource Sizing**
   - Start with t2.medium (AWS)
   - Scale based on usage
   - Use auto-scaling

2. **Caching**
   - Cache experiment stats
   - Use CDN for static assets
   - Implement Redis for session management

3. **Spot Instances**
   - Use spot instances for non-critical workloads
   - Implement graceful shutdown
   - Set up automatic failover