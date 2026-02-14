#!/bin/bash
set -e

# teardown.sh - Clean up TaskAI deployment from Kubernetes cluster
# Usage: ./teardown.sh [environment] [--force]
# Environment: local, dev, staging, prod (default: local)

ENVIRONMENT=${1:-local}
FORCE_FLAG=${2:-}
VALID_ENVIRONMENTS=("local" "dev" "staging" "prod")

# Validate environment
if [[ ! " ${VALID_ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    echo "❌ Error: Invalid environment '${ENVIRONMENT}'"
    echo "Valid environments: ${VALID_ENVIRONMENTS[*]}"
    exit 1
fi

echo "🧹 Tearing down TaskAI deployment (${ENVIRONMENT})..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Set namespace based on environment
NAMESPACE="taskai"
if [ "$ENVIRONMENT" == "dev" ]; then
    NAMESPACE="taskai-dev"
fi

# Verify cluster context
echo "📋 Current cluster context:"
kubectl config current-context
echo "📁 Target namespace: ${NAMESPACE}"
echo ""

# Safety confirmation (skip if --force flag is provided)
if [ "$FORCE_FLAG" != "--force" ]; then
    echo "⚠️  WARNING: This will delete all TaskAI resources in namespace ${NAMESPACE}"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "❌ Teardown cancelled"
        exit 0
    fi
fi

# Check if namespace exists
if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo "ℹ️  Namespace ${NAMESPACE} does not exist. Nothing to clean up."
    exit 0
fi

# Delete Helm release if it exists
if command -v helm &> /dev/null; then
    echo "🗑️  Checking for Helm releases..."
    if helm list --namespace=${NAMESPACE} | grep -q taskai; then
        echo "  Uninstalling Helm release..."
        helm uninstall taskai --namespace=${NAMESPACE}
        echo "✅ Helm release removed"
    fi
fi

# Delete Kubernetes resources
echo "🗑️  Deleting Kubernetes resources..."

# Delete ingress
echo "  Deleting ingress..."
kubectl delete ingress --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete services
echo "  Deleting services..."
kubectl delete service --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete deployments
echo "  Deleting deployments..."
kubectl delete deployment --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete Dapr subscriptions
echo "  Deleting Dapr subscriptions..."
kubectl delete subscription --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete Dapr components
echo "  Deleting Dapr components..."
kubectl delete component --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete ConfigMaps
echo "  Deleting ConfigMaps..."
kubectl delete configmap --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete Secrets
echo "  Deleting Secrets..."
kubectl delete secret --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete Kafka topics
echo "  Deleting Kafka topics..."
kubectl delete kafkatopic --all --namespace=${NAMESPACE} --ignore-not-found=true

# Delete Kafka cluster (optional - ask for confirmation)
if kubectl get kafka taskai-kafka --namespace=${NAMESPACE} &> /dev/null 2>&1; then
    if [ "$FORCE_FLAG" != "--force" ]; then
        echo ""
        read -p "Delete Kafka cluster? This will remove all message data. (yes/no): " kafka_confirm
        if [[ "$kafka_confirm" == "yes" ]]; then
            echo "  Deleting Kafka cluster..."
            kubectl delete kafka taskai-kafka --namespace=${NAMESPACE}
        fi
    else
        echo "  Deleting Kafka cluster..."
        kubectl delete kafka taskai-kafka --namespace=${NAMESPACE}
    fi
fi

# Wait for resources to be deleted
echo "⏳ Waiting for resources to be deleted..."
sleep 10

# Delete namespace (optional - ask for confirmation)
if [ "$FORCE_FLAG" != "--force" ]; then
    echo ""
    read -p "Delete namespace ${NAMESPACE}? This is irreversible. (yes/no): " namespace_confirm
    if [[ "$namespace_confirm" == "yes" ]]; then
        echo "  Deleting namespace..."
        kubectl delete namespace ${NAMESPACE}
        echo "✅ Namespace deleted"
    else
        echo "ℹ️  Namespace ${NAMESPACE} preserved"
    fi
else
    echo "  Deleting namespace..."
    kubectl delete namespace ${NAMESPACE}
    echo "✅ Namespace deleted"
fi

# Additional cleanup for local environment
if [ "$ENVIRONMENT" == "local" ]; then
    echo ""
    read -p "Stop Minikube cluster? (yes/no): " minikube_confirm
    if [[ "$minikube_confirm" == "yes" ]]; then
        echo "🛑 Stopping Minikube..."
        minikube stop
        echo "✅ Minikube stopped"

        echo ""
        read -p "Delete Minikube cluster completely? (yes/no): " delete_confirm
        if [[ "$delete_confirm" == "yes" ]]; then
            echo "🗑️  Deleting Minikube cluster..."
            minikube delete
            echo "✅ Minikube cluster deleted"
        fi
    fi
fi

# Uninstall Dapr (optional - only for local)
if [ "$ENVIRONMENT" == "local" ]; then
    echo ""
    read -p "Uninstall Dapr from cluster? (yes/no): " dapr_confirm
    if [[ "$dapr_confirm" == "yes" ]]; then
        if command -v dapr &> /dev/null; then
            echo "🗑️  Uninstalling Dapr..."
            dapr uninstall --kubernetes
            echo "✅ Dapr uninstalled"
        fi
    fi
fi

# Uninstall Strimzi operator (optional - only for local)
if [ "$ENVIRONMENT" == "local" ]; then
    echo ""
    read -p "Uninstall Strimzi operator? (yes/no): " strimzi_confirm
    if [[ "$strimzi_confirm" == "yes" ]]; then
        echo "🗑️  Uninstalling Strimzi operator..."
        kubectl delete namespace kafka --ignore-not-found=true
        echo "✅ Strimzi operator uninstalled"
    fi
fi

echo ""
echo "✅ Teardown complete!"
echo ""
echo "📊 Remaining resources:"
if kubectl get namespace ${NAMESPACE} &> /dev/null; then
    kubectl get all --namespace=${NAMESPACE}
else
    echo "  Namespace ${NAMESPACE} has been deleted"
fi

echo ""
echo "🔗 Useful commands:"
echo "  - View all namespaces: kubectl get namespaces"
echo "  - View cluster info: kubectl cluster-info"
if [ "$ENVIRONMENT" == "local" ]; then
    echo "  - Start Minikube: minikube start"
    echo "  - Redeploy: ./deploy-local.sh"
else
    echo "  - Redeploy: ./deploy-cloud.sh ${ENVIRONMENT}"
fi
