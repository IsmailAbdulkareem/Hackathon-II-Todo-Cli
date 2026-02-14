#!/bin/bash
set -e

# setup-minikube.sh - Initialize Minikube cluster for TaskAI
# Usage: ./setup-minikube.sh

echo "🚀 Setting up Minikube cluster for TaskAI..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: minikube is not installed"
    echo "Please install minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Start Minikube with recommended settings
echo "📦 Starting Minikube cluster..."
minikube start \
    --cpus=4 \
    --memory=8192 \
    --disk-size=20g \
    --driver=docker \
    --kubernetes-version=v1.28.0

# Enable required addons
echo "🔌 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Verify cluster is running
echo "✅ Verifying cluster status..."
kubectl cluster-info
kubectl get nodes

# Create namespaces
echo "📁 Creating namespaces..."
kubectl apply -f ../kubernetes/namespace.yaml

# Set default namespace to taskai
kubectl config set-context --current --namespace=taskai

echo ""
echo "✅ Minikube cluster setup complete!"
echo ""
echo "📊 Cluster Information:"
echo "  - Kubernetes Version: $(kubectl version --short | grep Server)"
echo "  - Nodes: $(kubectl get nodes --no-headers | wc -l)"
echo "  - Namespaces: taskai, taskai-dev"
echo ""
echo "🔗 Useful commands:"
echo "  - Dashboard: minikube dashboard"
echo "  - Tunnel (for LoadBalancer): minikube tunnel"
echo "  - Stop cluster: minikube stop"
echo "  - Delete cluster: minikube delete"
echo ""
echo "Next steps:"
echo "  1. Run ./install-dapr.sh to install Dapr"
echo "  2. Run ./install-kafka.sh to install Kafka"
echo "  3. Run ./deploy-local.sh to deploy TaskAI services"
