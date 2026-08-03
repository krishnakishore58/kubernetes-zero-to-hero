# Ingress + Egress + NGINX Controller + TLS + NetworkPolicy — Real-Time Demo

## Architecture Overview

```
Browser (HTTPS)
     │
     ▼
/etc/hosts  →  127.0.0.1  mystore.local
                           apparel.mystore.local
                           jewellery.mystore.local
     │
     ▼
minikube tunnel  (exposes LoadBalancer IP → localhost)
     │
     ▼
┌─────────────────────────────────────────────┐
│         ingress-nginx  (LoadBalancer SVC)    │  ← Ingress Controller
│         namespace: ingress-nginx             │    terminates TLS (port 443)
└──────────────┬──────────────────────────────┘
               │  matches Host / Path header
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│ apparel-svc │  │jewellery-svc │   ClusterIP Services (port 80)
│  (mystore)  │  │  (mystore)   │
└──────┬──────┘  └──────┬───────┘
       ▼                ▼
  apparel pods    jewellery pods    (port 8080, 2 replicas each)
```

---

## Routing Rules

### Path-Based  →  single domain, different paths
| URL | Service |
|-----|---------|
| `https://mystore.local/apparel` | apparel-svc |
| `https://mystore.local/jewellery` | jewellery-svc |

### Host-Based  →  different subdomains
| URL | Service |
|-----|---------|
| `https://apparel.mystore.local/apparel` | apparel-svc |
| `https://jewellery.mystore.local/jewellery` | jewellery-svc |

---

## NetworkPolicy Summary

| Direction | apparel pods | jewellery pods |
|-----------|-------------|----------------|
| Ingress   | Only from `ingress-nginx` controller pods | Same |
| Egress    | DNS (port 53) + intra-namespace only | Same |

This means: direct `curl` from another pod outside `ingress-nginx` namespace is **blocked**.

---

## Prerequisites

```bash
## Restart minikube with Calico
# Delete current cluster
minikube delete

# Start fresh with Calico CNI
minikube start --driver=docker --cni=calico

# Wait for Calico pods to be ready
kubectl wait --namespace kube-system \
  --for=condition=ready pod \
  --selector=k8s-app=calico-node \
  --timeout=120s

# Confirm Calico is running
kubectl get pods -n kube-system | grep calico

# Enable ingress addon (installs nginx ingress controller)
minikube addons enable ingress

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s

```
---

## Step 1 — Build & Load Docker Images into Minikube

```bash
# Point your shell to minikube's Docker daemon
eval $(minikube docker-env)

# Build both images
docker build -t apparel-api:latest   apps/apparel/
docker build -t jewellery-api:latest apps/jewellery/

# Verify images are available inside minikube
minikube image ls | grep -E "apparel|jewellery"
```

---

## Step 2 — Apply All Manifests

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-apparel.yaml
kubectl apply -f k8s/02-jewellery.yaml
kubectl apply -f k8s/03-tls-cert.yaml
kubectl apply -f k8s/04-ingress-path-based.yaml
kubectl apply -f k8s/05-ingress-host-based.yaml

minikube addons enable ingress
kubectl apply -f k8s/06-network-policy.yaml
```

---

## Step 3 — Verify Everything is Running

```bash
# Pods should be Running (2 replicas each)
kubectl get pods -n mystore

# Services
kubectl get svc -n mystore

# Ingress rules
kubectl get ingress -n mystore

# TLS certificate issued by cert-manager (READY=True)
kubectl get certificate -n mystore

# TLS secret created
kubectl get secret mystore-tls-secret -n mystore

# NetworkPolicies
kubectl get networkpolicy -n mystore
```

---

## Step 4 — Expose via minikube tunnel

```bash
# Run in a separate terminal — keeps the tunnel alive
minikube tunnel
```

Get the external IP assigned to the ingress controller:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
# Note the EXTERNAL-IP (usually 127.0.0.1 with minikube tunnel)
```

---

## Step 5 — Add /etc/hosts Entries

```bash
# Replace 127.0.0.1 with the EXTERNAL-IP from above if different
sudo sh -c 'echo "127.0.0.1 mystore.local apparel.mystore.local jewellery.mystore.local" >> /etc/hosts'
```

---

## Step 6 — Test in Browser or curl

### Path-Based Routing
```bash
# -k skips TLS verification for self-signed cert
curl -k https://mystore.local/apparel
curl -k https://mystore.local/jewellery
curl -k https://mystore.local/apparel/1
curl -k https://mystore.local/jewellery/2
```

### Host-Based Routing
```bash
curl -k https://apparel.mystore.local/apparel
curl -k https://jewellery.mystore.local/jewellery
```

### Browser
Open any of these in your browser (accept the self-signed cert warning):
- https://mystore.local/apparel
- https://mystore.local/jewellery
- https://apparel.mystore.local/apparel
- https://jewellery.mystore.local/jewellery

---

## Step 7 — Verify NetworkPolicy is Enforced

```bash
# Launch a test pod in default namespace (outside mystore)
kubectl run test-pod --image=curlimages/curl --restart=Never -it --rm -- \
  curl http://apparel-svc.mystore.svc.cluster.local/apparel
# Expected: connection timeout / refused — blocked by NetworkPolicy

# From inside mystore namespace — also blocked (not ingress-nginx)
kubectl run test-pod -n mystore --image=curlimages/curl --restart=Never -it --rm -- \
  curl http://apparel-svc/apparel
# Expected: blocked
```

---

## Step 8 — Cleanup

```bash
kubectl delete namespace mystore
kubectl delete clusterissuer selfsigned-issuer

# Remove /etc/hosts entries
sudo sed -i '' '/mystore.local/d' /etc/hosts
```

---

## Key Concepts Recap

| Concept | What it does here |
|---------|-------------------|
| **Ingress Controller (nginx)** | Single entry point, terminates TLS, routes by Host/Path |
| **Path-based Ingress** | `mystore.local/apparel` and `/jewellery` → different backends |
| **Host-based Ingress** | `apparel.mystore.local` vs `jewellery.mystore.local` → different backends |
| **cert-manager + ClusterIssuer** | Auto-issues self-signed TLS cert, stores in K8s Secret |
| **NetworkPolicy (Ingress)** | Only nginx controller pods can reach app pods on port 8080 |
| **NetworkPolicy (Egress)** | App pods can only do DNS lookups + talk within namespace |
