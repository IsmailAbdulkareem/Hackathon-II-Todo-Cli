#!/bin/bash
set -e

# install-dapr.sh - Install and configure Dapr on Kubernetes
# Usage: ./install-dapr.sh

echo "🎯 Installing Dapr on Kubernetes..."

# Check if dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ Error: Dapr CLI is not installed"
    echo "Please install Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: kubectl is not configured or cluster is not running"
    echo "Please run ./setup-minikube.sh first"
    exit 1
fi

# Initialize Dapr on Kubernetes
echo "📦 Initializing Dapr on Kubernetes cluster..."
dapr init --kubernetes --wait

# Verify Dapr installation
echo "✅ Verifying Dapr installation..."
dapr status --kubernetes

# Wait for Dapr system pods to be ready
echo "⏳ Waiting for Dapr system pods to be ready..."
kubectl wait --for=condition=ready pod \
    --all \
    --namespace=dapr-system \
    --timeout=300s

# Apply Dapr components
echo "🔧 Applying Dapr components..."
if [ -d "../dapr/components" ]; then
    kubectl apply -f ../dapr/components/ --namespace=taskai
    echo "✅ Dapr components applied to taskai namespace"
else
    echo "⚠️  Warning: Dapr components directory not found"
fi

# Apply Dapr subscriptions
echo "📬 Applying Dapr subscriptions..."
if [ -d "../dapr/subscriptions" ]; then
    kubectl apply -f ../dapr/subscriptions/ --namespace=taskai
    echo "✅ Dapr subscriptions applied to taskai namespace"
else
    echo "⚠️  Warning: Dapr subscriptions directory not found"
fi

# Display Dapr components
echo ""
echo "📋 Dapr Components in taskai namespace:"
kubectl get components --namespace=taskai 2>/dev/null || echo "  No components found yet"

echo ""
echo "✅ Dapr installation complete!"
echo ""
echo "📊 Dapr Information:"
echo "  - Version: $(dapr version | grep 'Runtime version')"
echo "  - Namespace: dapr-system"
echo "  - Components namespace: taskai"
echo ""
echo "🔗 Useful commands:"
echo "  - Check Dapr status: dapr status -k"
echo "  - View Dapr logs: kubectl logs -l app=dapr-sidecar-injector -n dapr-system"
echo "  - Uninstall Dapr: dapr uninstall -k"
echo ""
echo "Next steps:"
echo "  1. Run ./install-kafka.sh to install Kafka"
echo "  2. Run ./deploy-local.sh to deploy TaskAI services"
