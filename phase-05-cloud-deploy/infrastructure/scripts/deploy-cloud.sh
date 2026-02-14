#!/bin/bash
set -e

# deploy-cloud.sh - Deploy TaskAI to cloud Kubernetes cluster (AKS/GKE/EKS)
# Usage: ./deploy-cloud.sh [environment]
# Environment: dev, staging, prod (default: dev)

ENVIRONMENT=${1:-dev}
VALID_ENVIRONMENTS=("dev" "staging" "prod")

# Validate environment
if [[ ! " ${VALID_ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    echo "❌ Error: Invalid environment '${ENVIRONMENT}'"
    echo "Valid environments: ${VALID_ENVIRONMENTS[*]}"
    exit 1
fi

echo "🚀 Deploying TaskAI to cloud Kubernetes cluster (${ENVIRONMENT})..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: kubectl is not configured or cluster is not accessible"
    echo "Please configure kubectl to connect to your cloud cluster"
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Error: Helm is not installed"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Verify cluster context
echo "📋 Current cluster context:"
kubectl config current-context
echo ""
read -p "Is this the correct cluster for ${ENVIRONMENT} deployment? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Set namespace based on environment
NAMESPACE="taskai"
if [ "$ENVIRONMENT" == "dev" ]; then
    NAMESPACE="taskai-dev"
fi

# Create namespace if it doesn't exist
echo "📁 Creating namespace ${NAMESPACE}..."
kubectl create namespace ${NAMESPACE} 2>/dev/null || echo "Namespace ${NAMESPACE} already exists"

# Set namespace context
kubectl config set-context --current --namespace=${NAMESPACE}

# Check if Dapr is installed
echo "🔍 Checking Dapr installation..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo "⚠️  Dapr is not installed. Installing Dapr..."
    if command -v dapr &> /dev/null; then
        dapr init --kubernetes --wait
    else
        echo "❌ Error: Dapr CLI is not installed"
        echo "Please install Dapr: https://docs.dapr.io/getting-started/install-dapr-cli/"
        exit 1
    fi
fi

# Install/Upgrade Kafka using Strimzi (if not already installed)
echo "🔍 Checking Kafka installation..."
if ! kubectl get kafka taskai-kafka --namespace=${NAMESPACE} &> /dev/null 2>&1; then
    echo "⚠️  Kafka is not installed. Installing Kafka..."

    # Install Strimzi operator if not present
    if ! kubectl get namespace kafka &> /dev/null; then
        kubectl create namespace kafka
        kubectl create -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka

        # Wait for operator
        kubectl wait --for=condition=ready pod \
            -l name=strimzi-cluster-operator \
            --namespace=kafka \
            --timeout=300s
    fi

    # Apply Kafka cluster
    kubectl apply -f ../kafka/kafka-cluster.yaml --namespace=${NAMESPACE} || echo "Using default Kafka configuration"

    # Wait for Kafka
    kubectl wait kafka/taskai-kafka \
        --for=condition=Ready \
        --timeout=600s \
        --namespace=${NAMESPACE}
fi

# Validate secrets before deployment
echo "🔐 Validating secrets..."
echo "⚠️  IMPORTANT: Ensure all secrets are properly configured for ${ENVIRONMENT}"
echo ""
echo "Required secrets:"
echo "  - POSTGRES_USER"
echo "  - POSTGRES_PASSWORD"
echo "  - JWT_SECRET"
echo "  - OPENAI_API_KEY"
echo "  - RESEND_API_KEY"
echo ""
read -p "Have you configured all production secrets? (yes/no): " secrets_confirm
if [[ "$secrets_confirm" != "yes" ]]; then
    echo "❌ Deployment cancelled. Please configure secrets first."
    exit 1
fi

# Deploy using Helm (if Helm charts exist)
if [ -d "../helm/taskai" ]; then
    echo "📦 Deploying using Helm..."

    VALUES_FILE="../helm/taskai/values-${ENVIRONMENT}.yaml"
    if [ ! -f "$VALUES_FILE" ]; then
        VALUES_FILE="../helm/taskai/values.yaml"
        echo "⚠️  Environment-specific values file not found, using default values.yaml"
    fi

    helm upgrade --install taskai ../helm/taskai \
        --namespace=${NAMESPACE} \
        --values=${VALUES_FILE} \
        --wait \
        --timeout=10m

    echo "✅ Helm deployment complete"
else
    # Deploy using kubectl (fallback)
    echo "📦 Deploying using kubectl..."

    # Apply ConfigMaps
    echo "  Applying ConfigMaps..."
    kubectl apply -f ../kubernetes/configmap.yaml --namespace=${NAMESPACE}

    # Apply Secrets
    echo "  Applying Secrets..."
    kubectl apply -f ../kubernetes/secrets.yaml --namespace=${NAMESPACE}

    # Apply Dapr components
    echo "  Applying Dapr components..."
    kubectl apply -f ../dapr/components/ --namespace=${NAMESPACE}

    # Apply Dapr subscriptions
    echo "  Applying Dapr subscriptions..."
    kubectl apply -f ../dapr/subscriptions/ --namespace=${NAMESPACE}

    # Deploy services
    echo "  Deploying services..."
    kubectl apply -f ../kubernetes/deployments/ --namespace=${NAMESPACE}
    kubectl apply -f ../kubernetes/services/ --namespace=${NAMESPACE}

    # Apply ingress
    echo "  Applying ingress..."
    kubectl apply -f ../kubernetes/ingress/ingress.yaml --namespace=${NAMESPACE}

    echo "✅ kubectl deployment complete"
fi

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/backend-api --timeout=300s --namespace=${NAMESPACE}
kubectl wait --for=condition=available deployment/recurring-service --timeout=300s --namespace=${NAMESPACE}
kubectl wait --for=condition=available deployment/notification-service --timeout=300s --namespace=${NAMESPACE}
kubectl wait --for=condition=available deployment/frontend --timeout=300s --namespace=${NAMESPACE}

# Display deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get deployments --namespace=${NAMESPACE}
echo ""
kubectl get pods --namespace=${NAMESPACE}
echo ""
kubectl get services --namespace=${NAMESPACE}
echo ""
kubectl get ingress --namespace=${NAMESPACE}

# Get ingress information
INGRESS_IP=$(kubectl get ingress taskai-ingress --namespace=${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
INGRESS_HOSTNAME=$(kubectl get ingress taskai-ingress --namespace=${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

echo ""
echo "✅ TaskAI deployment to ${ENVIRONMENT} complete!"
echo ""
echo "🔗 Access Information:"
if [ "$INGRESS_IP" != "pending" ]; then
    echo "  - Ingress IP: ${INGRESS_IP}"
fi
if [ -n "$INGRESS_HOSTNAME" ]; then
    echo "  - Ingress Hostname: ${INGRESS_HOSTNAME}"
fi
echo "  - Namespace: ${NAMESPACE}"
echo ""
echo "📝 Next steps:"
echo "  1. Configure DNS to point to the ingress IP/hostname"
echo "  2. Set up TLS certificates (cert-manager recommended)"
echo "  3. Configure monitoring and alerting"
echo "  4. Set up backup and disaster recovery"
echo ""
echo "🔗 Useful commands:"
echo "  - View logs: kubectl logs -f deployment/<service-name> -n ${NAMESPACE}"
echo "  - View Dapr logs: kubectl logs -f deployment/<service-name> -c daprd -n ${NAMESPACE}"
echo "  - Scale deployment: kubectl scale deployment/<service-name> --replicas=N -n ${NAMESPACE}"
echo "  - Rollback: helm rollback taskai -n ${NAMESPACE} (if using Helm)"
echo ""
echo "🧹 To remove deployment: ./teardown.sh ${ENVIRONMENT}"
