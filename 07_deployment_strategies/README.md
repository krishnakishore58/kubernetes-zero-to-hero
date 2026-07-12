# Kubernetes Deployment Strategies

## Pre-requisites

```bash
# Start minikube
minikube start

# Build v1 image
docker build -t demo-app:1.0 ./app

# Modify main.py response to "hello from demo-app v2", then build v2
docker build -t demo-app:2.0 ./app

```

---

## 1. Rolling Update

**What is it?**
Kubernetes replaces old pods with new pods one (or a few) at a time. At any given moment, both old and new versions are running. Traffic is never fully interrupted.

**Real-time example:**
Think of a McDonald's drive-through with 4 billing counters. During a software upgrade, they upgrade one counter at a time — customers are always being served, they just don't notice the upgrade happening behind the scenes.

```bash
# Deploy v1
kubectl apply -f examples/01-rolling-update.yaml

# Watch pods in a separate terminal
kubectl get pods -w
kubectl get deployment

# Trigger rolling update to v2
kubectl set image deployment/demo-app-rolling demo-app=demo-app:2.0

# Watch the rollout progress
kubectl rollout status deployment/demo-app-rolling

# Rollback if something goes wrong
kubectl rollout undo deployment/demo-app-rolling

# Cleanup
kubectl delete -f examples/01-rolling-update.yaml
```

---

## 2. Recreate

**What is it?**
Kubernetes kills ALL existing pods first, then creates new pods. There is a period where zero pods are serving traffic — this means downtime.

**Real-time example:**
Think of a bank branch that closes for 2 hours on a Sunday to upgrade their core banking system. All customers are told "come back later". Simple, but there's a blackout window.

```bash
# Deploy v1
kubectl apply -f examples/02-recreate.yaml

# Watch pods in a separate terminal
kubectl get pods -w
kubectl get deployment

# Trigger update — watch ALL pods terminate, then new ones appear
kubectl set image deployment/demo-app-recreate demo-app=demo-app:2.0

# Notice the gap where 0/4 pods are ready
kubectl rollout status deployment/demo-app-recreate

# Cleanup
kubectl delete -f examples/02-recreate.yaml
```

---

## 3. Blue/Green

**What is it?**
You run two identical environments — Blue (current live) and Green (new version). Both are fully deployed. You switch traffic from Blue to Green by changing the service selector. Rollback is instant — just switch back.

**Real-time example:**
Think of a live TV broadcast with two studios. Studio A (Blue) is live on air. Studio B (Green) is fully set up and rehearsed. The director says "switch" — and in one second, viewers see Studio B. If something goes wrong, switch back to A immediately.

```bash
# Deploy both Blue and Green + service pointing to Blue
kubectl apply -f examples/03-blue-green.yaml

# Verify service is pointing to Blue
kubectl get svc demo-app-svc -o jsonpath='{.spec.selector.slot}'
# Output: blue

# Test — traffic goes to v1 (Blue)
minikube tunnel (leave the session running)
curl http://localhost:80/

# CUTOVER: Switch traffic to Green (one command!)
kubectl patch svc demo-app-svc -p '{"spec":{"selector":{"slot":"green"}}}'

# Test — traffic now goes to v2 (Green)
curl http://localhost:80/

# ROLLBACK: Switch back to Blue
kubectl patch svc demo-app-svc -p '{"spec":{"selector":{"slot":"blue"}}}'

# Cleanup
kubectl delete -f examples/03-blue-green.yaml
```

---

## 4. Canary

**What is it?**
You deploy the new version alongside the old version but with very few replicas. Since the service selects both, traffic is split by pod ratio. If 9 pods run v1 and 1 pod runs v2, roughly 10% of users hit v2. If v2 is healthy, you gradually increase its replicas.

**Real-time example:**
Think of a food delivery app rolling out a new checkout flow. They show it to only 10% of users first. If complaints go up or conversion drops, they kill it. If metrics look good, they roll it out to 50%, then 100%.

```bash
# Deploy stable (9 replicas) + canary (1 replica)
kubectl apply -f examples/04-canary.yaml

# See all pods — 9 stable + 1 canary
kubectl get pods -l app=demo-app --show-labels

# Test — curl multiple times, ~10% responses will be from v2
for i in $(seq 1 10); do curl -s http://localhost:80/; echo; done

# Promote canary — scale up canary, scale down stable
kubectl scale deployment demo-app-canary --replicas=5
kubectl scale deployment demo-app-stable --replicas=5

# Full promotion
kubectl scale deployment demo-app-canary --replicas=10
kubectl scale deployment demo-app-stable --replicas=0

# Cleanup
kubectl delete -f examples/04-canary.yaml
```

---


## Quick Reference

| Strategy | Downtime | Rollback Speed | Infra Cost | K8s Native | Best For |
|----------|----------|----------------|------------|------------|----------|
| Rolling Update | None | Slow (re-roll) | 1x | ✅ | Most workloads |
| Recreate | Yes | Slow | 1x | ✅ | DB migrations, breaking changes |
| Blue/Green | None | Instant | 2x | ✅ | Critical apps needing instant rollback |
| Canary | None | Fast | 1.1x | ✅ | Validating stability with real traffic |

