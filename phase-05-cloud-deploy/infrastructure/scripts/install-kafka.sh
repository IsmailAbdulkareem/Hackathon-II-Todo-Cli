#!/bin/bash
set -e

# install-kafka.sh - Install Kafka using Strimzi operator on Kubernetes
# Usage: ./install-kafka.sh

echo "📨 Installing Kafka using Strimzi operator..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: kubectl is not configured or cluster is not running"
    echo "Please run ./setup-minikube.sh first"
    exit 1
fi

# Install Strimzi operator
echo "📦 Installing Strimzi operator..."
kubectl create namespace kafka 2>/dev/null || echo "Namespace kafka already exists"

# Apply Strimzi operator installation files
STRIMZI_VERSION="0.39.0"
echo "📥 Downloading Strimzi ${STRIMZI_VERSION}..."
kubectl create -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka

# Wait for Strimzi operator to be ready
echo "⏳ Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=ready pod \
    -l name=strimzi-cluster-operator \
    --namespace=kafka \
    --timeout=300s

# Apply Kafka cluster configuration
echo "🔧 Creating Kafka cluster..."
if [ -f "../kafka/kafka-cluster.yaml" ]; then
    kubectl apply -f ../kafka/kafka-cluster.yaml --namespace=taskai
else
    # Create a basic Kafka cluster if config doesn't exist
    cat <<EOF | kubectl apply -f - --namespace=taskai
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskai-kafka
  namespace: taskai
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF
fi

# Wait for Kafka cluster to be ready
echo "⏳ Waiting for Kafka cluster to be ready (this may take a few minutes)..."
kubectl wait kafka/taskai-kafka \
    --for=condition=Ready \
    --timeout=600s \
    --namespace=taskai

# Create Kafka topics
echo "📋 Creating Kafka topics..."
cat <<EOF | kubectl apply -f - --namespace=taskai
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: taskai
  labels:
    strimzi.io/cluster: taskai-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: taskai
  labels:
    strimzi.io/cluster: taskai-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
EOF

# Wait for topics to be ready
echo "⏳ Waiting for Kafka topics to be ready..."
sleep 10

# Display Kafka resources
echo ""
echo "📋 Kafka Resources in taskai namespace:"
kubectl get kafka --namespace=taskai
echo ""
kubectl get kafkatopic --namespace=taskai

echo ""
echo "✅ Kafka installation complete!"
echo ""
echo "📊 Kafka Information:"
echo "  - Cluster: taskai-kafka"
echo "  - Namespace: taskai"
echo "  - Bootstrap servers: taskai-kafka-kafka-bootstrap.taskai.svc.cluster.local:9092"
echo "  - Topics: task-events, reminders"
echo ""
echo "🔗 Useful commands:"
echo "  - View Kafka pods: kubectl get pods -l strimzi.io/cluster=taskai-kafka -n taskai"
echo "  - View Kafka logs: kubectl logs -l strimzi.io/name=taskai-kafka-kafka -n taskai"
echo "  - List topics: kubectl get kafkatopic -n taskai"
echo ""
echo "Next steps:"
echo "  1. Run ./deploy-local.sh to deploy TaskAI services"
