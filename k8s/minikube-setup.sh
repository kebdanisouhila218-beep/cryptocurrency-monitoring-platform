#!/bin/bash
# Minikube Setup for CryptoTracker

echo "🚀 Setting up Minikube for CryptoTracker..."

# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Set up port forwarding
echo "📊 Setting up port forwarding..."
minikube service crypto-api-service --url
minikube service crypto-frontend-service --url

# Build and push images to Minikube
echo "🐳 Building Docker images for Minikube..."
eval $(minikube docker-env)

# Build API image
docker build -t crypto-api:latest ./api

# Build Collector image  
docker build -t crypto-collector:latest ./collector

# Build Frontend image
docker build -t crypto-frontend:latest ./frontend

# Deploy to Minikube
echo "🚀 Deploying to Minikube..."
kubectl apply -f k8s/deployment.yml

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=crypto-api -n crypto-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=crypto-frontend -n crypto-platform --timeout=300s

# Show status
echo "📋 Deployment status:"
kubectl get pods -n crypto-platform
kubectl get services -n crypto-platform

echo "✅ Minikube setup complete!"
echo "🌐 Access URLs:"
echo "   API: $(minikube service crypto-api-service --url)"
echo "   Frontend: $(minikube service crypto-frontend-service --url)"
echo "   Grafana: http://localhost:3001"
echo "   Prometheus: http://localhost:9090"
