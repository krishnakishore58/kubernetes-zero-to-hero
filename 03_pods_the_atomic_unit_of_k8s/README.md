# Pods — The Atomic Unit of Kubernetes

---

## Topics Covered

- Pod vs Container
- Single-Container vs Multi-Container Pod
- Pod Lifecycle (`Pending → Running → Succeeded/Failed`)
  - Init Containers
  - Sidecar / Ambassador Patterns
  - Ephemeral Storage
- Static Pods
- Pod Networking Basics

---

## 1. Pod vs Container

| | Container | Pod |
|---|-----------|-----|
| **Definition** | A single application process built from a Docker image | Kubernetes smallest deployable unit, wraps one or more containers |
| **IP Address** | No dedicated IP | Gets a unique IP address |
| **Storage** | No shared volumes | Shared volumes across containers |
| **Networking** | Isolated | Containers share `localhost` (`127.0.0.1`) |

### **Example of a Container (Docker)**
```bash
docker run nginx:latest
```

### **Example of a Pod (Kubernetes)**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

### **Key Points**
- You **never deploy containers directly** in Kubernetes — you deploy Pods
- Pods share **network and storage** among their containers
- Containers inside a Pod communicate via `localhost`
- Each Pod gets a **single IP address**

---

## 2. Single-Container vs Multi-Container Pod

### **A) Single-Container Pod**
One application per Pod. Runs your primary application.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
spec:
  containers:
    - name: app
      image: myapp:1.0
```

---

### **B) Multi-Container Pod**
Multiple containers in one Pod that share:
- Same IP address
- Same `localhost`
- Same volumes

**Real-World Example:**  
A web application container writes log files to a shared volume, and a **sidecar** container in the same Pod reads those logs and forwards them to a central logging service.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app-with-logging
spec:
  containers:
    - name: app
      image: myapp:1.0
    - name: log-collector
      image: fluentd:latest
```

---

## 3. Pod Lifecycle

### **Lifecycle States**

| State | Description |
|-------|-------------|
| **Pending** | Pod accepted by Kubernetes; scheduling or pulling images |
| **Running** | All containers have started |
| **Succeeded** | All containers terminated successfully |
| **Failed** | At least one container terminated with an error |

---

### **A) Init Containers**
Run **before** the main application containers start. Used for setup tasks.

**Common Use Cases:**
- Wait for a database to be ready
- Download configuration before the app starts

```yaml
spec:
  initContainers:
    - name: init-db
      image: busybox
      command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 1; done']
  containers:
    - name: app
      image: myapp:1.0
```

---

### **B) Sidecar Pattern**
A helper container that runs **alongside** the main application container.

**Common Use Cases:**
- Log forwarding
- Metrics collection
- Config synchronization

```yaml
spec:
  containers:
    - name: app
      image: myapp:1.0
      volumeMounts:
        - name: logs
          mountPath: /var/log
    - name: log-shipper
      image: fluentd
      volumeMounts:
        - name: logs
          mountPath: /var/log
```

---

### **C) Ambassador Pattern**
A **proxy container** that handles network traffic on behalf of the main application container.

**Common Use Cases:**
- App talks to a local proxy; proxy connects to an external service
- TLS termination
- Traffic routing

```yaml
spec:
  containers:
    - name: app
      image: myapp:1.0
    - name: ambassador
      image: envoyproxy/envoy
      ports:
        - containerPort: 8080
```

---

### **D) Ephemeral Storage**
Temporary storage inside a Pod. **Lost when the Pod is deleted.**

**Common Use Cases:**
- Cache files
- Temporary uploads
- Logs stored in the container filesystem

```yaml
spec:
  containers:
    - name: cache
      image: redis
      volumeMounts:
        - name: cache-volume
          mountPath: /data
  volumes:
    - name: cache-volume
      emptyDir: {}
```

---

## 4. Static Pods

Pods managed **directly by the Kubelet**, not by the API Server or Controller Manager.

### **Use Cases**
- Running control plane components: `kube-apiserver`, `scheduler`, `etcd`

### **How It Works**
- Place a manifest file at the node path: `/etc/kubernetes/manifests/`
- Kubelet automatically detects and creates the Pod

```yaml
# /etc/kubernetes/manifests/static-nginx.yaml
apiVersion: v1
kind: Pod
metadata:
  name: static-nginx
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

> **Note:** Static Pods are visible via `kubectl get pods` but cannot be managed using `kubectl delete`.

---

## 5. Pod Networking Basics

- Every Pod gets its **own unique IP address**
- Containers within the same Pod share:
  - Network namespace
  - `localhost`
  - Port space

### **Container Communication**

| Scenario | How They Communicate |
|----------|---------------------|
| **Same Pod** | Via `localhost` and port number |
| **Different Pods** | Via Pod IP addresses or Kubernetes Services |

### **Same Pod Communication**
```
Backend listening on port 8080
→ Frontend reaches backend at localhost:8080
```

### **Different Pod Communication**
```yaml
# Pod 1 — Backend
metadata:
  name: backend
spec:
  containers:
    - name: api
      ports:
        - containerPort: 8080

# Pod 2 — Frontend (accessing Pod 1 via IP)
spec:
  containers:
    - name: frontend
      env:
        - name: BACKEND_URL
          value: "http://10.244.1.5:8080"  # Pod 1's IP
```

> **Best Practice:** Use **Kubernetes Services** instead of hardcoding Pod IPs, as Pod IPs change when Pods are restarted.

---

## 6. Demo: Hands-On Examples

### **Demo 1: Single-Container Pod (Nginx)**

```yaml
# single-container-pod-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: single-container-pod-demo
spec:
  containers:
    - name: nginx
      image: nginx:alpine
```

```bash
# Deploy the Pod
kubectl apply -f single-container-pod-demo.yaml

# Check Pod status
kubectl get pod nginx-pod -o wide
```

---

### **Demo 2: Multi-Container Pod (App + Sidecar)**

A Pod with:
- A **web-server** container (Nginx)
- A **web-client** sidecar container that periodically curls the web server

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod-demo
  labels:
    app: simple-demo
spec:
  containers:
  # Web server
  - name: web-server
    image: nginx:alpine
    ports:
    - containerPort: 80
  # Client that talks to web server
  - name: web-client
    image: curlimages/curl:latest
    command: ["/bin/sh", "-c"]
    args:
      - |
        echo "This container will call the web-server container every 3 seconds"
        echo "Both containers are in the same Pod, so they share network namespace"
        echo "================================================================"
        while true; do
          echo "[$(date)] Calling web-server at http://localhost:80..."
          curl -s http://localhost:80 | grep -o "<title>[^<]*</title>"
          sleep 3
        done
```

```bash
# Deploy the Pod
kubectl apply -f multi-container-pod-demo.yaml

# Check Pod status
kubectl get pod multi-container-pod-demo -o wide

# View logs from the curl client (proves container-to-container communication)
kubectl logs multi-container-pod-demo web-client --tail=10

# Execute into the nginx container to verify it's serving
kubectl exec multi-container-pod-demo -c web-server -- curl -s http://localhost:80/ | head -5
```

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| **Pod vs Container** | Pods wrap containers and provide shared networking and storage |
| **Single-Container Pod** | One app per Pod — the most common pattern |
| **Multi-Container Pod** | Tightly coupled containers sharing network and storage |
| **Init Containers** | Run setup tasks before the main app starts |
| **Sidecar Pattern** | Helper container alongside the main app |
| **Ambassador Pattern** | Proxy container managing network traffic |
| **Ephemeral Storage** | Temporary storage lost when the Pod is deleted |
| **Static Pods** | Managed by Kubelet directly, used for control plane components |
| **Pod Networking** | Every Pod gets a unique IP; use Services for reliable communication |

---

## References

- [Kubernetes Pods Documentation](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Pod Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)