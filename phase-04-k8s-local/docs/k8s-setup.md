# Kubernetes Cluster Setup Documentation

**Feature**: Phase IV - Local Kubernetes Deployment
**Date**: 2026-01-28
**Status**: ✅ Cluster Running

## Cluster Configuration

### Minikube Startup Command

```bash
minikube start --cpus=2 --memory=3072 --driver=docker
```

**Resource Allocation**:
- CPUs: 2 cores
- Memory: 3072 MB (3 GB)
- Driver: Docker Desktop

## Verification Outputs

### 1. Cluster Status (T010)

```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

**Status**: ✅ All components running and healthy

### 2. Node Status (T011)

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   55s   v1.34.0
```

**Verification**:
- ✅ Node name: minikube
- ✅ Status: Ready
- ✅ Role: control-plane
- ✅ Kubernetes version: v1.34.0

### 3. Cluster Version (T012)

```
Client Version: v1.35.0
Kustomize Version: v5.7.1
Server Version: v1.34.0
```

**Verification**:
- ✅ kubectl client: v1.35.0
- ✅ Kubernetes server: v1.34.0
- ✅ Kustomize: v5.7.1

## Prerequisites Installed

### Docker
```
Docker version 29.1.3, build f52814d
```
✅ Running

### kubectl
```
Client Version: v1.35.0
```
✅ Installed

### Minikube
```
minikube version: v1.37.0
```
✅ Installed

### Helm
```
version.BuildInfo{Version:"v4.0.0", ...}
```
✅ Installed

## Cluster Access

### Context Configuration

```bash
minikube update-context
```

Output:
```
* "minikube" context has been updated to point to 127.0.0.1:56151
* Current context is "minikube"
```

### Verify Access

```bash
kubectl cluster-info
```

The cluster is accessible at: `https://127.0.0.1:56151`

## Success Criteria Verification

- ✅ **SC-001**: Cluster setup completed in under 10 minutes
- ✅ Cluster starts successfully and shows healthy status
- ✅ At least one node is available and ready (minikube node)
- ✅ Cluster responds with version information (v1.34.0)
- ✅ kubectl configured and can communicate with cluster

## Troubleshooting Notes

### Issue: Stale kubectl context
**Solution**: Run `minikube update-context` to fix kubeconfig

### Issue: Slow startup
**Cause**: First-time download of base image (488 MB) and Kubernetes preload
**Duration**: ~5-10 minutes depending on network speed

## Next Steps

Phase 2 Complete ✅

Ready for Phase 3: Application Containerization
- Build Docker images for frontend and backend
- Use AI assistance (Docker AI/Gordon) for Dockerfile generation
- Store images in Minikube's local Docker registry

## Cluster Management Commands

### Start cluster
```bash
minikube start
```

### Stop cluster
```bash
minikube stop
```

### Delete cluster
```bash
minikube delete
```

### Check status
```bash
minikube status
kubectl get nodes
kubectl cluster-info
```

### Access dashboard
```bash
minikube dashboard
```

## Environment Configuration

To use Minikube's Docker daemon (required for Phase 3):

```bash
# Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Git Bash / WSL
eval $(minikube docker-env)
```

This allows Docker images built locally to be used directly by Minikube without pushing to an external registry.
