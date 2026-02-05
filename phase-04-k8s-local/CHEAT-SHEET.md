# 🎬 ONE-PAGE RECORDING CHEAT SHEET (PowerShell)

**Keep this open during recording - Copy & Paste these commands**

---

## ✅ PRE-RECORDING CHECK
```powershell
minikube status
kubectl get pods
```
**All pods should show "1/1 Running"**

---

## 🎥 RECORDING COMMANDS (In Order)

### 1. SHOW DOCKER IMAGES
```powershell
docker images | findstr todo
```

### 2. SHOW DOCKERFILE
```powershell
Get-Content phase-04-k8s-local\frontend\Dockerfile
```

### 3. SHOW CLUSTER STATUS
```powershell
minikube status
kubectl get nodes
kubectl cluster-info
```

### 4. SHOW HELM RELEASES
```powershell
helm list
```

### 5. SHOW ALL RESOURCES
```powershell
kubectl get all
```

### 6. SHOW PODS
```powershell
kubectl get pods
```

### 7. SHOW SERVICES
```powershell
kubectl get services
```

### 8. SHOW CONFIGMAPS
```powershell
kubectl get configmaps
```

### 9. SHOW SECRETS
```powershell
kubectl get secrets | findstr todo
```

### 10. DESCRIBE CONFIGMAP
```powershell
kubectl describe configmap todo-frontend-config
```

### 11. SHOW FRONTEND LOGS
```powershell
kubectl logs -l app=todo-frontend --tail=10
```

### 12. SHOW BACKEND LOGS
```powershell
kubectl logs -l app=todo-backend --tail=10
```

### 13. GET FRONTEND URL (KEEP TERMINAL OPEN!)
```powershell
minikube service todo-frontend --url
```
**Copy the URL and open in browser**

### 14. SCALE TO 5 REPLICAS
```powershell
kubectl scale deployment todo-frontend --replicas=5
kubectl get pods | findstr todo-frontend
```

### 15. SCALE BACK TO 3
```powershell
kubectl scale deployment todo-frontend --replicas=3
kubectl get pods | findstr todo-frontend
```

### 16. SHOW HELM CHART
```powershell
Get-ChildItem phase-04-k8s-local\k8s\helm\todo-frontend
```

### 17. SHOW DOCUMENTATION
```powershell
Get-ChildItem phase-04-k8s-local
```

### 18. FINAL SUMMARY
```powershell
kubectl get all
```

---

## 🎤 WHAT TO SAY (Brief Version)

1. "Showing Docker images - frontend 1GB, backend 390MB"
2. "Multi-stage Dockerfile with security best practices"
3. "Minikube cluster running, node ready"
4. "Applications deployed via Helm charts"
5. "All Kubernetes resources: pods, services, deployments"
6. "4 pods running: 1 backend, 3 frontend replicas"
7. "Services expose applications on ports 3000 and 8000"
8. "ConfigMaps for non-sensitive configuration"
9. "Secrets for sensitive data like database credentials"
10. "Frontend configuration shows API URL"
11. "Frontend logs show Next.js running"
12. "Backend logs show FastAPI running"
13. "Accessing application via Minikube service"
14. "Scaling to 5 replicas - Kubernetes makes this easy"
15. "Scaling back to 3 replicas"
16. "Helm chart structure with templates"
17. "Comprehensive documentation included"
18. "Summary: Phase IV complete - containerization and Kubernetes deployment successful"

---

## ⚡ QUICK TROUBLESHOOTING

**If Minikube stopped:**
```powershell
minikube start --cpus=4 --memory=3500
```

**If service URL doesn't work:**
```powershell
kubectl port-forward svc/todo-frontend 8080:3000
```
Then open: http://localhost:8080

**If you need to restart:**
```powershell
kubectl get pods
kubectl get services
```

---

## ✅ SUCCESS CHECKLIST

Before recording:
- [ ] Minikube is running
- [ ] All 4 pods show "Running"
- [ ] Terminal font is large
- [ ] Browser is ready
- [ ] This cheat sheet is open

During recording:
- [ ] Speak clearly
- [ ] Show command output
- [ ] Explain what you're doing
- [ ] Don't rush

---

**TOTAL TIME: 10-15 minutes**
**YOU'VE GOT THIS! 🚀**
