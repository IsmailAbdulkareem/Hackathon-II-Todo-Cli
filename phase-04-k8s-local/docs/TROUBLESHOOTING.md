# Troubleshooting: Backend Not Accessible from Browser

## Issue
Frontend loads but cannot connect to backend API.

## Root Cause
The environment variable `NEXT_PUBLIC_API_URL=http://todo-backend:7860` uses Kubernetes internal DNS, which only works **inside the cluster**. Your browser (running on your host machine) cannot resolve `todo-backend`.

## Solutions

### Option 1: Expose Backend via NodePort (Quick Fix)
Change backend service to NodePort so browser can access it:

```bash
# Edit values.yaml
kubectl patch service todo-backend -p '{"spec":{"type":"NodePort"}}'

# Get backend URL
minikube service todo-backend --url

# Update frontend to use this URL
# Example: http://192.168.49.2:30860
```

### Option 2: Use Minikube Tunnel (Recommended for Local Dev)
```bash
# In a separate terminal, run:
minikube tunnel

# This makes LoadBalancer services accessible on localhost
```

### Option 3: Server-Side API Calls (Production Pattern)
The frontend should make API calls server-side (Next.js API routes) instead of client-side. This way, the Next.js server (running in the pod) can reach the backend via internal DNS.

## Current Status
- ✅ Backend pod running and healthy
- ✅ Backend accessible from frontend pod (internal)
- ❌ Backend not accessible from browser (external)

## Quick Test
```bash
# Test from inside cluster (works)
kubectl exec deployment/todo-frontend -- wget -qO- http://todo-backend:7860/

# Test from browser (fails)
# Open browser console and try: fetch('http://todo-backend:7860/')
# Error: DNS resolution fails
```

## For Hackathon Demo
**Current setup is correct for Kubernetes!** The issue is architectural:
- Backend is ClusterIP (internal only) - this is correct
- Frontend makes client-side API calls - this won't work with ClusterIP

**For demo purposes**, you can:
1. Show that both pods are running
2. Show that backend is accessible from frontend pod
3. Explain this is a known limitation of client-side API calls in Kubernetes
4. In production, you'd use server-side API routes or expose backend via Ingress
