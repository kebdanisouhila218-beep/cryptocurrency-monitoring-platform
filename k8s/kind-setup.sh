#!/bin/bash
# Kind Setup for CryptoTracker

echo "🚀 Setting up Kind cluster for CryptoTracker..."

# Create Kind cluster
kind create cluster --config kind-config.yaml

# Load Docker images into Kind
echo "🐳 Loading Docker images into Kind..."
kind load docker-image crypto-api:latest
kind load docker-image crypto-collector:latest
kind load docker-image crypto-frontend:latest
kind load docker-image mongo:6
kind load docker-image redis:7-alpine
kind load docker-image prom/prometheus:v2.47.0
kind load docker-image grafana/grafana:10.1.0
kind load docker-image percona/mongodb_exporter:0.39
kind load docker-image oliver006/redis_exporter:v1.55.0
kind load docker-image prom/node-exporter:v1.6.1

# Deploy applications
echo "🚀 Deploying to Kind..."
kubectl apply -f k8s/deployment.yml

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=crypto-api -n crypto-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=crypto-frontend -n crypto-platform --timeout=300s

# Show status
echo "📋 Deployment status:"
kubectl get pods -n crypto-platform
kubectl get services -n crypto-platform

echo "✅ Kind setup complete!"
echo "🌐 Access URLs:"
echo "   API: http://localhost:8000"
echo "   Frontend: http://localhost:80"
echo "   Grafana: http://localhost:3001"
echo "   Prometheus: http://localhost:9090"
