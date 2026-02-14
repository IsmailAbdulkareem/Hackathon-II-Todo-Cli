# TaskAI Deployment Guide

## Overview

This guide covers deploying TaskAI to both local (Minikube) and cloud (AKS/GKE/EKS) Kubernetes clusters. TaskAI uses a microservices architecture with Dapr, Kafka, and PostgreSQL.

## Prerequisites

### Required Tools

- **kubectl** (v1.28+): Kubernetes command-line tool
- **Docker** (v24+): Container runtime
- **Helm** (v3.12+): Kubernetes package manager (optional but recommended)
- **Dapr CLI** (v1.12+): Dapr command-line tool

### For Local Deployment

- **Minikube** (v1.32+): Local Kubernetes cluster
- **Minimum Resources**: 4 CPU cores, 8GB RAM, 20GB disk space

### For Cloud Deployment

- **Cloud CLI**: Azure CLI, gcloud, or AWS CLI
- **Cloud Account**: Active subscription with appropriate permissions
- **Domain Name**: For production deployments (optional for dev)

## Local Deployment (Minikube)

### Step 1: Setup Minikube Cluster

```bash
cd infrastructure/scripts
chmod +x *.sh
./setup-minikube.sh
```

This script will:
- Start Minikube with recommended settings (4 CPUs, 8GB RAM)
- Enable required addons (ingress, metrics-server, dashboard)
- Create namespaces (taskai, taskai-dev)
- Set default namespace to taskai

**Verify cluster**:
```bash
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Dapr

```bash
./install-dapr.sh
```

This script will:
- Initialize Dapr on Kubernetes
- Apply Dapr components (Pub/Sub, State Store, Secrets)
- Apply Dapr subscriptions for services
- Wait for Dapr system pods to be ready

**Verify Dapr**:
```bash
dapr status -k
kubectl get pods -n dapr-system
```

### Step 3: Install Kafka

```bash
./install-kafka.sh
```

This script will:
- Install Strimzi operator
- Create Kafka cluster (taskai-kafka)
- Create Kafka topics (task-events, reminders)
- Wait for Kafka cluster to be ready

**Verify Kafka**:
```bash
kubectl get kafka -n taskai
kubectl get kafkatopic -n taskai
kubectl get pods -l strimzi.io/cluster=taskai-kafka -n taskai
```

### Step 4: Configure Secrets

Before deploying, update the secrets in `infrastructure/kubernetes/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: taskai-secrets
  namespace: taskai
type: Opaque
stringData:
  POSTGRES_USER: "taskai"
  POSTGRES_PASSWORD: "CHANGE_ME_PRODUCTION"  # ← Change this
  JWT_SECRET: "CHANGE_ME_PRODUCTION"         # ← Change this
  OPENAI_API_KEY: "sk-..."                   # ← Add your key
  RESEND_API_KEY: "re_..."                   # ← Add your key
```

**Generate secure secrets**:
```bash
# Generate JWT secret
openssl rand -base64 32

# Generate PostgreSQL password
openssl rand -base64 24
```

### Step 5: Deploy TaskAI Services

```bash
./deploy-local.sh
```

This script will:
- Build Docker images using Minikube's Docker daemon
- Apply ConfigMaps and Secrets
- Deploy all services (backend-api, recurring-service, notification-service, frontend)
- Apply Kubernetes Services and Ingress
- Wait for all deployments to be ready

**Monitor deployment**:
```bash
# Watch pods starting
kubectl get pods -w

# Check deployment status
kubectl get deployments

# View logs
kubectl logs -f deployment/backend-api
kubectl logs -f deployment/backend-api -c daprd  # Dapr sidecar logs
```

### Step 6: Access the Application

Add the Minikube IP to your hosts file:

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (Linux/Mac)
echo "$(minikube ip) taskai.local" | sudo tee -a /etc/hosts

# Add to C:\Windows\System32\drivers\etc\hosts (Windows - as Administrator)
# <minikube-ip> taskai.local
```

**Access URLs**:
- Frontend: http://taskai.local
- Backend API: http://taskai.local/api
- Health Check: http://taskai.local/health

**Alternative (Port Forwarding)**:
```bash
# Forward frontend
kubectl port-forward service/frontend 3000:3000

# Forward backend API
kubectl port-forward service/backend-api-service 8000:8000

# Access via localhost
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

### Step 7: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# Test health endpoint
curl http://taskai.local/health

# View Minikube dashboard
minikube dashboard
```

## Cloud Deployment

### Prerequisites

1. **Kubernetes Cluster**: Create a managed Kubernetes cluster
   - **Azure (AKS)**: `az aks create`
   - **Google Cloud (GKE)**: `gcloud container clusters create`
   - **AWS (EKS)**: `eksctl create cluster`

2. **kubectl Context**: Configure kubectl to connect to your cluster
   ```bash
   # Azure
   az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

   # Google Cloud
   gcloud container clusters get-credentials myGKECluster --zone us-central1-a

   # AWS
   aws eks update-kubeconfig --name myEKSCluster --region us-east-1
   ```

3. **Container Registry**: Set up a container registry
   - **Azure**: Azure Container Registry (ACR)
   - **Google Cloud**: Google Container Registry (GCR)
   - **AWS**: Elastic Container Registry (ECR)

### Step 1: Build and Push Docker Images

```bash
# Set your registry URL
REGISTRY="your-registry.azurecr.io"  # or gcr.io/project-id or account.dkr.ecr.region.amazonaws.com

# Login to registry
docker login $REGISTRY

# Build and push images
cd services/backend-api
docker build -t $REGISTRY/taskai/backend-api:latest .
docker push $REGISTRY/taskai/backend-api:latest

cd ../recurring-service
docker build -t $REGISTRY/taskai/recurring-service:latest .
docker push $REGISTRY/taskai/recurring-service:latest

cd ../notification-service
docker build -t $REGISTRY/taskai/notification-service:latest .
docker push $REGISTRY/taskai/notification-service:latest

cd ../frontend
docker build -t $REGISTRY/taskai/frontend:latest .
docker push $REGISTRY/taskai/frontend:latest
```

### Step 2: Update Image References

Update deployment manifests to use your registry:

```yaml
# infrastructure/kubernetes/deployments/backend-api.yaml
spec:
  template:
    spec:
      containers:
      - name: backend-api
        image: your-registry.azurecr.io/taskai/backend-api:latest
        imagePullPolicy: Always
```

Or use Helm values:

```yaml
# infrastructure/helm/taskai/values-prod.yaml
image:
  registry: your-registry.azurecr.io
  pullPolicy: Always
```

### Step 3: Configure Production Secrets

**CRITICAL**: Never commit production secrets to Git!

```bash
# Create secrets from files or environment variables
kubectl create secret generic taskai-secrets \
  --from-literal=POSTGRES_USER=taskai \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 24) \
  --from-literal=JWT_SECRET=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  --from-literal=RESEND_API_KEY=$RESEND_API_KEY \
  --namespace=taskai
```

**Best Practice**: Use cloud-native secret management:
- **Azure**: Azure Key Vault with CSI driver
- **Google Cloud**: Secret Manager with CSI driver
- **AWS**: Secrets Manager with CSI driver

### Step 4: Deploy to Cloud

```bash
cd infrastructure/scripts
./deploy-cloud.sh prod
```

The script will:
1. Verify cluster context
2. Install Dapr (if not present)
3. Install Kafka using Strimzi
4. Validate secrets configuration
5. Deploy using Helm or kubectl
6. Wait for all deployments to be ready

**Monitor deployment**:
```bash
kubectl get pods -n taskai -w
kubectl get deployments -n taskai
kubectl get services -n taskai
kubectl get ingress -n taskai
```

### Step 5: Configure DNS and TLS

#### DNS Configuration

Get the ingress IP or hostname:

```bash
kubectl get ingress taskai-ingress -n taskai
```

Create DNS records:
- **A Record**: `taskai.yourdomain.com` → `<ingress-ip>`
- **CNAME**: `taskai.yourdomain.com` → `<ingress-hostname>`

#### TLS Certificate (cert-manager)

Install cert-manager:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

Create ClusterIssuer:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Update ingress for TLS:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taskai-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - taskai.yourdomain.com
    secretName: taskai-tls
  rules:
  - host: taskai.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
```

### Step 6: Configure Monitoring

#### Prometheus & Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Default credentials: admin / prom-operator
```

#### Dapr Dashboard

```bash
# Install Dapr dashboard
dapr dashboard -k -p 9999

# Access at http://localhost:9999
```

### Step 7: Configure Backups

#### Database Backups

```bash
# Create CronJob for PostgreSQL backups
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: taskai
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - pg_dump -h postgres -U taskai taskai | gzip > /backup/taskai-\$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: taskai-secrets
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: postgres-backup-pvc
          restartPolicy: OnFailure
EOF
```

## Scaling

### Horizontal Pod Autoscaler (HPA)

```bash
# Enable metrics server (if not already enabled)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create HPA for backend-api
kubectl autoscale deployment backend-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  --namespace=taskai

# Create HPA for frontend
kubectl autoscale deployment frontend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  --namespace=taskai

# View HPA status
kubectl get hpa -n taskai
```

### Manual Scaling

```bash
# Scale backend-api to 5 replicas
kubectl scale deployment backend-api --replicas=5 -n taskai

# Scale frontend to 3 replicas
kubectl scale deployment frontend --replicas=3 -n taskai
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n taskai

# Describe pod for events
kubectl describe pod <pod-name> -n taskai

# View pod logs
kubectl logs <pod-name> -n taskai
kubectl logs <pod-name> -c daprd -n taskai  # Dapr sidecar logs

# Check resource constraints
kubectl top pods -n taskai
```

### Service Connectivity Issues

```bash
# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod:
wget -O- http://backend-api-service.taskai.svc.cluster.local:8000/health

# Check service endpoints
kubectl get endpoints -n taskai

# Check Dapr components
kubectl get components -n taskai
```

### Kafka Issues

```bash
# Check Kafka cluster status
kubectl get kafka taskai-kafka -n taskai

# View Kafka logs
kubectl logs -l strimzi.io/name=taskai-kafka-kafka -n taskai

# Check topics
kubectl get kafkatopic -n taskai

# Describe topic
kubectl describe kafkatopic task-events -n taskai
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm psql --image=postgres:15 --restart=Never -- \
  psql -h postgres -U taskai -d taskai

# Check database logs
kubectl logs deployment/postgres -n taskai
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n taskai
kubectl describe ingress taskai-ingress -n taskai

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Test ingress from inside cluster
kubectl run -it --rm curl --image=curlimages/curl --restart=Never -- \
  curl -H "Host: taskai.local" http://taskai-ingress.taskai.svc.cluster.local
```

## Rollback

### Using kubectl

```bash
# View deployment history
kubectl rollout history deployment/backend-api -n taskai

# Rollback to previous version
kubectl rollout undo deployment/backend-api -n taskai

# Rollback to specific revision
kubectl rollout undo deployment/backend-api --to-revision=2 -n taskai
```

### Using Helm

```bash
# View release history
helm history taskai -n taskai

# Rollback to previous release
helm rollback taskai -n taskai

# Rollback to specific revision
helm rollback taskai 2 -n taskai
```

## Cleanup

### Remove Deployment

```bash
cd infrastructure/scripts
./teardown.sh local   # For Minikube
./teardown.sh prod    # For cloud deployment
```

### Manual Cleanup

```bash
# Delete all resources in namespace
kubectl delete all --all -n taskai

# Delete namespace
kubectl delete namespace taskai

# Uninstall Dapr
dapr uninstall -k

# Delete Kafka cluster
kubectl delete kafka taskai-kafka -n taskai

# Uninstall Strimzi operator
kubectl delete namespace kafka
```

## Best Practices

1. **Use Helm for Production**: Easier upgrades and rollbacks
2. **Separate Environments**: Use different namespaces (dev, staging, prod)
3. **Resource Limits**: Always set CPU and memory limits
4. **Health Checks**: Configure liveness and readiness probes
5. **Secrets Management**: Use cloud-native secret stores
6. **Monitoring**: Set up Prometheus and Grafana
7. **Logging**: Use centralized logging (ELK, Loki)
8. **Backups**: Automate database and configuration backups
9. **CI/CD**: Automate deployments with GitHub Actions or similar
10. **Security**: Enable network policies, RBAC, and pod security policies

## Next Steps

- [Local Development Guide](local-development.md)
- [API Reference](api-reference.md)
- [Architecture Documentation](architecture.md)
- [MCP Tools Guide](mcp-tools.md)

---

**Last Updated**: 2026-02-14
**Version**: 1.0.0
