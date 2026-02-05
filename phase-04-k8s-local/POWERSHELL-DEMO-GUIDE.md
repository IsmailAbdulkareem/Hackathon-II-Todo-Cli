# 🎬 VIDEO DEMO GUIDE - POWERSHELL VERSION

**For Windows PowerShell Users**
**Status**: ✅ ALL SYSTEMS OPERATIONAL
**Recording Time**: 10-15 minutes

---

## 🚀 POWERSHELL COMMANDS FOR YOUR VIDEO

### PART 1: Introduction (30 seconds)
**Say**: "Hello, I'm demonstrating Phase IV: Local Kubernetes Deployment for the Todo Chatbot project."

---

### PART 2: Show Docker Images (1 minute)

```powershell
# Show Docker images
docker images | Select-String "todo"
```

**Alternative (more reliable):**
```powershell
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | Select-String "todo"
```

**Or use findstr (Windows native):**
```powershell
docker images | findstr todo
```

**Say**: "Here are the containerized applications: frontend (1.01GB) and backend (390MB)."

```powershell
# Show Dockerfile
Get-Content phase-04-k8s-local\frontend\Dockerfile
```

**Say**: "This Dockerfile shows multi-stage build with security best practices."

---

### PART 3: Kubernetes Cluster Status (1 minute)

```powershell
# Check Minikube status
minikube status

# Check nodes
kubectl get nodes

# Check cluster info
kubectl cluster-info
```

**Say**: "The Minikube cluster is running with all components healthy."

---

### PART 4: Show Deployments (2 minutes)

```powershell
# List Helm releases
helm list

# Show all Kubernetes resources
kubectl get all

# Show pods
kubectl get pods

# Show services
kubectl get services
```

**Say**: "All applications deployed via Helm. We have 4 pods running: 1 backend and 3 frontend replicas."

---

### PART 5: Configuration Management (1 minute)

```powershell
# Show ConfigMaps
kubectl get configmaps

# Show Secrets
kubectl get secrets | Select-String "todo"

# Describe ConfigMap
kubectl describe configmap todo-frontend-config
```

**Say**: "Configuration managed through ConfigMaps and Secrets."

---

### PART 6: Show Application Logs (1 minute)

```powershell
# Frontend logs
kubectl logs -l app=todo-frontend --tail=10

# Backend logs
kubectl logs -l app=todo-backend --tail=10
```

**Say**: "Application logs show both services running successfully."

---

### PART 7: Access the Application (2 minutes)

```powershell
# Get frontend URL (keep this terminal open!)
minikube service todo-frontend --url
```

**Action**:
1. Keep that terminal open
2. Copy the URL (e.g., http://127.0.0.1:xxxxx)
3. Open it in your browser
4. Show the application running

**Say**: "Here's the Todo Chatbot running inside Kubernetes."

---

### PART 8: Demonstrate Scaling (2 minutes)

```powershell
# Scale up to 5 replicas
kubectl scale deployment todo-frontend --replicas=5

# Check pods
kubectl get pods | Select-String "todo-frontend"

# Scale back to 3
kubectl scale deployment todo-frontend --replicas=3

# Verify
kubectl get pods | Select-String "todo-frontend"
```

**Say**: "Kubernetes makes scaling effortless. Scaled to 5 replicas and back to 3."

---

### PART 9: Show Helm Chart Structure (1 minute)

```powershell
# Show directory structure
Get-ChildItem phase-04-k8s-local\k8s\helm\todo-frontend

# Show values file
Get-Content phase-04-k8s-local\k8s\helm\todo-frontend\values.yaml
```

**Say**: "Here's the Helm chart structure with configurable values."

---

### PART 10: Show Documentation (1 minute)

```powershell
# List files
Get-ChildItem phase-04-k8s-local

# Show README (first 50 lines)
Get-Content phase-04-k8s-local\README.md | Select-Object -First 50
```

**Say**: "Comprehensive documentation for deployment and operations."

---

### PART 11: Final Summary (1 minute)

```powershell
# Show all resources
kubectl get all
```

**Say**: "Phase IV demonstrates:
- ✅ Docker containerization
- ✅ Kubernetes cluster with Minikube
- ✅ Helm-based deployment
- ✅ All pods running and ready
- ✅ Application accessible
- ✅ Scaling capabilities
- ✅ Complete documentation

Phase IV is complete. Thank you."

---

## 📋 QUICK COPY-PASTE COMMANDS (PowerShell)

```powershell
# Show images
docker images | findstr todo

# Show cluster
minikube status
kubectl get nodes
kubectl cluster-info

# Show deployments
helm list
kubectl get all
kubectl get pods
kubectl get services

# Show config
kubectl get configmaps
kubectl get secrets | findstr todo

# Show logs
kubectl logs -l app=todo-frontend --tail=10
kubectl logs -l app=todo-backend --tail=10

# Access app (keep terminal open!)
minikube service todo-frontend --url

# Scale demo
kubectl scale deployment todo-frontend --replicas=5
kubectl get pods | findstr todo-frontend
kubectl scale deployment todo-frontend --replicas=3
kubectl get pods | findstr todo-frontend

# Show structure
Get-ChildItem phase-04-k8s-local
Get-Content phase-04-k8s-local\README.md | Select-Object -First 50
```

---

## 💡 POWERSHELL TIPS

### If you want to use grep-like commands:

**Option 1: Use Select-String (PowerShell native)**
```powershell
docker images | Select-String "todo"
kubectl get pods | Select-String "frontend"
```

**Option 2: Use findstr (Windows native)**
```powershell
docker images | findstr todo
kubectl get pods | findstr frontend
```

**Option 3: Use Where-Object (PowerShell filtering)**
```powershell
docker images | Where-Object { $_ -match "todo" }
```

### Alternative: Use Git Bash
If you have Git installed, you can use Git Bash which supports Linux commands like `grep`, `cat`, `head`, `tail`, etc.

---

## ✅ YOU'RE READY TO RECORD!

**All systems operational:**
- ✅ Docker images built
- ✅ Minikube cluster running
- ✅ All pods ready (1/1 and 3/3)
- ✅ Services accessible
- ✅ Application works in browser

**Just follow the PowerShell commands above. Good luck! 🎬🚀**
