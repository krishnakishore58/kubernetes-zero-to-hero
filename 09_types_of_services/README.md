# Kubernetes Service Types — Demo Guide

A hands-on walkthrough of the four core Kubernetes service types using an nginx deployment.

---

## Base Deployment

All services below target the same deployment (`deployment.yaml`) — an nginx pod labeled `app: demo-app` on container port `80`.

---

## 1. ClusterIP (`ClusterIP_Service.yaml`)

**Problem:** Pods get ephemeral IPs that change on every restart. Other pods inside the cluster can't reliably communicate with them.

**Solution:** ClusterIP assigns a stable virtual IP accessible only within the cluster. Acts as the internal DNS entry point for pod-to-pod communication.

**Key points:**
- Default service type
- Accessible only inside the cluster
- Use case: microservice-to-microservice communication

```bash
# Works from inside the cluster
kubectl exec -it <any-pod> -- curl demo-app-clusterip:8080

# Not reachable from outside — by design

kubectl port-forward pod/<pod-name> 8080:80
kubectl port-forward svc/demo-app-clusterip 8080:8080 - even for port forwarding why we should still be preferring for Service is because the pod name changes after restart

kubectl run curlpod --rm -i --image=curlimages/curl:latest -- curl http://<pod-ip>>:80

kubectl run curlpod --rm -i --image=curlimages/curl:latest -- curl http://demo-app-clusterip:8080

kubectl run curlpod --rm -i --image=curlimages/curl:latest -- curl http://demo-app-clusterip.default.svc.cluster.local:8080

```

---

## 2. NodePort (`NodePort_Service.yaml`)

**Problem:** ClusterIP is internal-only. During development/testing you need quick external access without provisioning a cloud load balancer.

**Solution:** Opens a static port (`30080`) on every node's IP. External traffic hitting `<NodeIP>:30080` is forwarded to the service.

**Key points:**
- Port range: `30000–32767`
- Every node exposes the port — not ideal for production
- Use case: local dev, quick demos, on-prem clusters without a cloud LB

```bash
curl http://<NodeIP>:30080
```

---

## 3. LoadBalancer (`LoadBalancer_Service.yaml`)

**Problem:** NodePort exposes raw node IPs and ports — no single entry point, no DNS, no HA, not production-grade.

**Solution:** Provisions a cloud-native load balancer (AWS NLB/ALB, GCP, Azure) automatically. You get a single external IP or DNS hostname.

**Key points:**
- Superset of NodePort — also opens a NodePort internally
- Cloud provider handles LB provisioning
- On local clusters: requires `minikube tunnel` or MetalLB
- Use case: production workloads needing external traffic

```bash
kubectl get svc demo-app-lb   # Watch EXTERNAL-IP get assigned
curl http://<EXTERNAL-IP>:8080
```

---

## 4. ExternalName (`ExternalName_Service.yaml`)

**Problem:** Apps inside the cluster need to reach external services (RDS, third-party APIs). Hardcoding external URLs in application code or ConfigMaps creates tight coupling and makes environment switching painful.

**Solution:** Creates a DNS CNAME alias inside the cluster. Pods reference the service name; Kubernetes resolves it to the external hostname — no proxying, no IP involved.

**Key points:**
- No selector, no pods, no proxying — pure DNS alias
- Swap the `externalName` to change the target with zero code changes
- Use case: abstracting external databases, SaaS APIs, cross-namespace routing

```bash
# Inside a pod — resolves to httpbin.org (or your RDS endpoint in prod)
curl http://demo-external-svc/get

# Real-world externalName value:
# my-rds-prod.cxyz123.us-east-1.rds.amazonaws.com
```

---

## Quick Comparison

| Type         | Accessible From     | Use Case                          |
|--------------|---------------------|-----------------------------------|
| ClusterIP    | Inside cluster only | Pod-to-pod communication          |
| NodePort     | Node IP + port      | Dev/test, on-prem without cloud LB|
| LoadBalancer | External IP/DNS     | Production external traffic       |
| ExternalName | Inside cluster only | Abstracting external dependencies |
