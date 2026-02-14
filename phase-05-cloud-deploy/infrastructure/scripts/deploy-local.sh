#!/bin/bash
set -e

# deploy-local.sh - Deploy TaskAI services to local Minikube cluster
# Usage: ./deploy-local.sh

echo "🚀 Deploying TaskAI to local Minikube cluster..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: kubectl is not configured or cluster is not running"
    echo "Please run ./setup-minikube.sh first"
    exit 1
fi

# Check if Dapr is installed
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo "❌ Error: Dapr is not installed"
    echo "Please run ./install-dapr.sh first"
    exit 1
fi

# Check if Kafka is installed
if ! kubectl get kafka taskai-kafka --namespace=taskai &> /dev/null 2>&1; then
    echo "❌ Error: Kafka cluster is not installed"
    echo "Please run ./install-kafka.sh first"
    exit 1
fi

# Set namespace context
kubectl config set-context --current --namespace=taskai

# Apply ConfigMaps
echo "📝 Applying ConfigMaps..."
kubectl apply -f ../kubernetes/configmap.yaml

# Apply Secrets
echo "🔐 Applying Secrets..."
kubectl apply -f ../kubernetes/secrets.yaml

echo "⚠️  WARNING: Default secrets are placeholders. Update them before production deployment!"

# Build Docker images (if running locally)
echo "🐳 Building Docker images..."
echo "Note: For Minikube, we'll use the Minikube Docker daemon"

# Point to Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend-api image
echo "  Building backend-api..."
cd ../../services/backend-api
docker build -t taskai/backend-api:latest .

# Build recurring-service image
echo "  Building recurring-service..."
cd ../recurring-service
docker build -t taskai/recurring-service:latest .

# Build notification-service image
echo "  Building notification-service..."
cd ../notification-service
docker build -t taskai/notification-service:latest .

# Build frontend image
echo "  Building frontend..."
cd ../frontend
docker build -t taskai/frontend:latest .

# Return to scripts directory
cd ../../infrastructure/scripts

# Apply Dapr components
echo "🔧 Applying Dapr components..."
kubectl apply -f ../dapr/components/ --namespace=taskai

# Apply Dapr subscriptions
echo "📬 Applying Dapr subscriptions..."
kubectl apply -f ../dapr/subscriptions/ --namespace=taskai

# Deploy services
echo "🚢 Deploying services..."

# Deploy backend-api
echo "  Deploying backend-api..."
kubectl apply -f ../kubernetes/deployments/backend-api.yaml
kubectl apply -f ../kubernetes/services/backend-api-service.yaml

# Deploy recurring-service
echo "  Deploying recurring-service..."
kubectl apply -f ../kubernetes/deployments/recurring-service.yaml
kubectl apply -f ../kubernetes/services/recurring-service.yaml

# Deploy notification-service
echo "  Deploying notification-service..."
kubectl apply -f ../kubernetes/deployments/notification-service.yaml
kubectl apply -f ../kubernetes/services/notification-service.yaml

# Deploy frontend
echo "  Deploying frontend..."
kubectl apply -f ../kubernetes/deployments/frontend.yaml
kubectl apply -f ../kubernetes/services/frontend-service.yaml

# Apply ingress
echo "🌐 Applying ingress..."
kubectl apply -f ../kubernetes/ingress/ingress.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/backend-api --timeout=300s
kubectl wait --for=condition=available deployment/recurring-service --timeout=300s
kubectl wait --for=condition=available deployment/notification-service --timeout=300s
kubectl wait --for=condition=available deployment/frontend --timeout=300s

# Display deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get deployments
echo ""
kubectl get pods
echo ""
kubectl get services
echo ""
kubectl get ingress

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Add entry to /etc/hosts (requires manual step)
echo ""
echo "✅ TaskAI deployment complete!"
echo ""
echo "🔗 Access Information:"
echo "  - Minikube IP: ${MINIKUBE_IP}"
echo "  - Frontend: http://taskai.local (after adding to /etc/hosts)"
echo "  - Backend API: http://taskai.local/api"
echo "  - Health Check: http://taskai.local/health"
echo ""
echo "📝 To access the application, add this line to your /etc/hosts file:"
echo "  ${MINIKUBE_IP} taskai.local"
echo ""
echo "  On Linux/Mac: sudo echo '${MINIKUBE_IP} taskai.local' >> /etc/hosts"
echo "  On Windows: Add '${MINIKUBE_IP} taskai.local' to C:\\Windows\\System32\\drivers\\etc\\hosts"
echo ""
echo "🔗 Useful commands:"
echo "  - View logs: kubectl logs -f deployment/<service-name>"
echo "  - View Dapr logs: kubectl logs -f deployment/<service-name> -c daprd"
echo "  - Port forward: kubectl port-forward service/frontend 3000:3000"
echo "  - Dashboard: minikube dashboard"
echo "  - Tunnel (for LoadBalancer): minikube tunnel"
echo ""
echo "🧹 To remove deployment: ./teardown.sh"
