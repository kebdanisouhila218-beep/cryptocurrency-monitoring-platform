# 🚀 Déploiement Kubernetes - CryptoTracker

## Vue d'ensemble

Ce document décrit le déploiement complet de CryptoTracker sur Kubernetes avec monitoring avancé, logging centralisé et health checks.

---

## 📋 Prérequis

### Outils requis
```bash
# Kubernetes local
minikube version  # ou kind version

# Docker
docker --version

# kubectl
kubectl version --client

# Helm (optionnel)
helm version
```

### Ressources système recommandées
- **CPU** : 4+ cores
- **Mémoire** : 8GB+ RAM
- **Stockage** : 20GB+ disque

---

## 🎯 Options de déploiement

### 1. Minikube (Recommandé pour développement)

#### Installation
```bash
# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Démarrage
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

#### Déploiement
```bash
# Script automatisé
chmod +x k8s/minikube-setup.sh
./k8s/minikube-setup.sh

# Ou manuel
kubectl apply -f k8s/deployment.yml
```

#### Accès
```bash
# URLs
minikube service crypto-api-service --url
minikube service crypto-frontend-service --url

# Dashboard
minikube dashboard
```

---

### 2. Kind (Kubernetes in Docker)

#### Installation
```bash
# Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

#### Déploiement
```bash
# Script automatisé
chmod +x k8s/kind-setup.sh
./k8s/kind-setup.sh

# Ou manuel
kind create cluster --config k8s/kind-config.yaml
kubectl apply -f k8s/deployment.yml
```

#### Accès
```bash
# Services
kubectl port-forward service/crypto-api-service 8000:80
kubectl port-forward service/crypto-frontend-service 3000:80
```

---

### 3. Cluster Cloud (Production)

#### Préparation
```bash
# Créer namespace
kubectl create namespace crypto-platform

# Secrets
kubectl create secret generic crypto-secrets \
  --from-literal=secret-key=YOUR_SECRET_KEY \
  -n crypto-platform

# ConfigMaps
kubectl create configmap crypto-config \
  --from-file=api/config.py \
  -n crypto-platform
```

#### Déploiement
```bash
# Appliquer les manifests
kubectl apply -f k8s/deployment.yml

# Monitoring
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana/
kubectl apply -f monitoring/loki/
```

---

## 📊 Architecture Kubernetes

### Services déployés

| Service | Réplicas | Port | Description |
|---------|-----------|------|-------------|
| **MongoDB** | 1 | 27017 | Base de données principale |
| **Redis** | 1 | 6379 | Cache et file de messages |
| **API** | 3 | 8000 | FastAPI backend |
| **Collector** | 1 | - | Service de collecte de données |
| **Frontend** | 2 | 80 | React SPA |
| **Prometheus** | 1 | 9090 | Monitoring |
| **Grafana** | 1 | 3001 | Visualisation |
| **Loki** | 1 | 3100 | Logs centralisés |

### Ingress et Load Balancing

```yaml
# Ingress pour routing externe
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: crypto-ingress
  namespace: crypto-platform
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - crypto-platform.example.com
    secretName: crypto-tls
  rules:
  - host: crypto-platform.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: crypto-frontend-service
            port:
              number: 80
  - host: api.crypto-platform.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: crypto-api-service
            port:
              number: 80
```

---

## 🔧 Configuration détaillée

### Variables d'environnement

```yaml
env:
- name: MONGO_HOST
  value: "mongodb-service"
- name: MONGO_PORT
  value: "27017"
- name: REDIS_HOST
  value: "redis-service"
- name: REDIS_PORT
  value: "6379"
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: crypto-secrets
      key: secret-key
- name: ENVIRONMENT
  value: "production"
- name: LOG_LEVEL
  value: "INFO"
```

### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health/liveness
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/readiness
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Auto-scaling

```yaml
# HPA pour l'API
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: crypto-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: crypto-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 📈 Monitoring et Observabilité

### Prometheus Metrics

```python
# Endpoints disponibles
GET /metrics                    # Métriques Prometheus
GET /health                    # Health check basique
GET /health/detailed           # Health check détaillé
GET /health/readiness          # Readiness probe
GET /health/liveness           # Liveness probe
```

### AlertManager

```yaml
# Règles d'alerte
- alert: APIDown
  expr: up{job="fastapi"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Crypto API is down"
    description: "Crypto API has been down for more than 1 minute"
```

### Grafana Dashboards

- **Crypto Platform Overview** : Vue générale du système
- **API Performance** : Métriques de performance API
- **Database Health** : État MongoDB et Redis
- **System Resources** : CPU, mémoire, disque

---

## 📝 Logs centralisés

### Loki Stack

```bash
# Démarrer Loki
docker-compose -f monitoring/loki/docker-compose.yml up -d

# Configuration Promtail
# monitoring/loki/promtail-config.yaml
```

### Types de logs collectés

1. **Application logs** : Logs de l'API et collector
2. **System logs** : Logs système des pods
3. **Access logs** : Logs d'accès Nginx/Ingress
4. **Error logs** : Logs d'erreurs détaillés

---

## 🔒 Sécurité

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: crypto-network-policy
  namespace: crypto-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### Secrets Management

```bash
# Créer des secrets
kubectl create secret generic crypto-secrets \
  --from-literal=secret-key=$(openssl rand -base64 32) \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  -n crypto-platform

# Secrets TLS
kubectl create secret tls crypto-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n crypto-platform
```

---

## 🚀 Déploiement complet

### Script de déploiement automatisé

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Déploiement CryptoTracker sur Kubernetes..."

# 1. Préparation
kubectl create namespace crypto-platform --dry-run=client -o yaml | kubectl apply -f -

# 2. Secrets
kubectl create secret generic crypto-secrets \
  --from-literal=secret-key=$SECRET_KEY \
  --from-literal=jwt-secret=$JWT_SECRET \
  -n crypto-platform --dry-run=client -o yaml | kubectl apply -f -

# 3. Application
kubectl apply -f k8s/deployment.yml

# 4. Monitoring
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana/

# 5. Attendre le déploiement
kubectl wait --for=condition=ready pod -l app=crypto-api -n crypto-platform --timeout=300s

echo "✅ Déploiement terminé!"
echo "🌐 Accès:"
echo "   API: $(kubectl get ingress crypto-ingress -n crypto-platform -o jsonpath='{.spec.rules[0].host}')"
echo "   Grafana: $(kubectl get ingress grafana-ingress -n monitoring -o jsonpath='{.spec.rules[0].host}')"
```

---

## 📊 Gestion et Maintenance

### Commandes utiles

```bash
# Vérifier le statut
kubectl get pods -n crypto-platform
kubectl get services -n crypto-platform
kubectl get ingress -n crypto-platform

# Logs
kubectl logs -f deployment/crypto-api -n crypto-platform
kubectl logs -f deployment/mongodb -n crypto-platform

# Scale
kubectl scale deployment crypto-api --replicas=5 -n crypto-platform

# Mise à jour
kubectl set image deployment/crypto-api api=crypto-api:v2.0.1 -n crypto-platform

# Rollback
kubectl rollout undo deployment/crypto-api -n crypto-platform
```

### Backup et Recovery

```bash
# Backup MongoDB
kubectl exec -it deployment/mongodb -n crypto-platform -- mongodump --out /backup

# Backup ConfigMaps
kubectl get configmap -n crypto-platform -o yaml > backup-configmaps.yaml

# Restore
kubectl exec -it deployment/mongodb -n crypto-platform -- mongorestore /backup
```

---

## 🔍 Dépannage

### Problèmes courants

1. **Pods en CrashLoopBackOff**
   ```bash
   kubectl describe pod <pod-name> -n crypto-platform
   kubectl logs <pod-name> -n crypto-platform --previous
   ```

2. **Services inaccessibles**
   ```bash
   kubectl get endpoints -n crypto-platform
   kubectl describe service <service-name> -n crypto-platform
   ```

3. **Ingress non fonctionnel**
   ```bash
   kubectl get ingress -n crypto-platform
   kubectl describe ingress <ingress-name> -n crypto-platform
   ```

### Performance

```bash
# Resource usage
kubectl top pods -n crypto-platform
kubectl top nodes

# Events
kubectl get events -n crypto-platform --sort-by='.lastTimestamp'
```

---

## 📚 Références

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Guide](https://minikube.sigs.k8s.io/docs/)
- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

---

## 🎯 Prochaines étapes

1. **CI/CD** : Intégrer avec GitHub Actions
2. **GitOps** : Utiliser ArgoCD ou Flux
3. **Multi-cluster** : Déploiement sur plusieurs clusters
4. **Disaster Recovery** : Configuration multi-région
5. **Security** : Pod Security Policies, RBAC avancé
