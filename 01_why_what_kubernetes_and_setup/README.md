# Kubernetes: Introduction, Setup & Important Files

---

## Problem Statement: Why Do We Need Kubernetes?

As modern applications grow, they are broken into multiple **microservices**, each running in its own container. Managing these containers manually becomes increasingly complex and error-prone.

### **Key Challenges Without Kubernetes:**

| Challenge | Description |
|-----------|-------------|
| **Container Management** | Managing hundreds or thousands of containers manually is difficult |
| **Scaling & High Availability** | Ensuring apps can handle traffic spikes and survive failures is hard |
| **Automated Deployments** | Rolling updates, rollbacks, and zero-downtime deployments are complex |
| **Resource Optimization** | Efficiently allocating CPU, memory across multiple machines is tedious |
| **Service Discovery & Load Balancing** | Identifying and routing traffic to the right containers is challenging |

---

## What is Orchestration?

**Orchestration** refers to the integration and automation of multiple services, allowing them to communicate, synchronize, and work seamlessly together.

**Example:**  
If you have **6 microservices** for an application, each running in its own container, communication between them becomes complex. Orchestration solves this by enabling all containers to work together seamlessly, automating their deployment, networking, and scaling.

---

## What is Kubernetes?

**Kubernetes (K8s)** is an open-source container **orchestration platform** that automates the deployment, scaling, and management of containerized applications in production environments.

- Originally developed by **Google**
- Now hosted by the **Cloud Native Computing Foundation (CNCF)**
- Uses a **declarative approach** (you describe the desired state, Kubernetes ensures it)

### **Key Concepts:**

| Concept | Description |
|---------|-------------|
| **Pod** | Smallest deployable unit, contains one or more containers |
| **Node** | A worker machine (VM or physical) that runs Pods |
| **Cluster** | A set of Nodes managed by Kubernetes |
| **Deployment** | Manages the desired state of your application |
| **Service** | Exposes your app to the network |
| **Namespace** | Logical separation of resources within a cluster |
| **ConfigMap** | Stores non-sensitive configuration data |
| **Secret** | Stores sensitive data like passwords and API keys |
| **Ingress** | Manages external access to services |

---

## Setting Up Kubernetes Locally with Minikube

**Minikube** lets you run a single-node Kubernetes cluster on your local machine for development and testing.

---

### **Setup on Linux (Ubuntu/Debian)**

```bash
# Step 1: Update system
sudo apt update && sudo apt upgrade -y

# Step 2: Download Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64

# Step 3: Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64

# Step 4: Start Minikube
minikube start

# Step 5: Set up kubectl alias
alias kubectl="minikube kubectl --"

# Step 6: Verify the cluster
kubectl get pods -A

# Step 7: Open Minikube Dashboard
minikube dashboard
```

### **Useful Minikube Commands**
```bash
# Start Minikube
minikube start

# Stop Minikube
minikube stop

# Pause Minikube (without deleting resources)
minikube pause

# Unpause Minikube
minikube unpause

# Delete Minikube cluster
minikube delete

# Get Minikube IP
minikube ip

# Enable Ingress addon
minikube addons enable ingress

# List all addons
minikube addons list
```

## **kubeconfig File** ##  
The kubeconfig file is the most important configuration file in Kubernetes. It stores information about:

Clusters: The Kubernetes clusters you can connect to
Users: Credentials for authenticating to clusters
Contexts: Combinations of cluster and user, making it easy to switch between environments
Default location: ~/.kube/config

```yaml
apiVersion: v1
kind: Config
clusters:
  - name: minikube
    cluster:
      server: https://192.168.49.2:8443
users:
  - name: minikube
    user:
      client-certificate: /path/to/cert
      client-key: /path/to/key
contexts:
  - name: minikube
    context:
      cluster: minikube
      user: minikube
current-context: minikube
```
