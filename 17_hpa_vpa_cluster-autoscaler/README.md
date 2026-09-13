# Autoscaling demo — HPA (CPU), VPA (memory) and Cluster Autoscaler (minikube)

Purpose
- Hands‑on demo showing best‑practice split: HPA controls CPU/throughput (replicas) and VPA controls memory (vertical sizing). Also covers how node capacity (Cluster Autoscaler) fits in.
- Includes practical verification steps, safety controls (PDB, LimitRange), and alerts for frequent evictions.

Prereqs (Minikube on WSL)
- Minikube running and kubectl targeting it.
- Metrics Server installed:
  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
- VPA components installed (recommender, updater, admission webhook). Example helper:
  git clone https://github.com/kubernetes/autoscaler.git
  bash autoscaler/vertical-pod-autoscaler/hack/vpa-up.sh
- (Optional) Prometheus + kube-state-metrics for monitoring/alerts and Cluster Autoscaler/Karpenter for cloud autoscaling.

Quick apply
1. Create namespace and app:  
   `kubectl apply -f namespace.yaml`  
   `kubectl apply -f demo-app-deployment.yaml`

2. HPA:  
   `kubectl apply -f hpa.yaml`

3. VPA (start in Off to collect recommendations):  
   `kubectl apply -f vpa-object.yaml`

4. Generate load when ready:  
   `kubectl apply -f load-generator.yaml`

What to observe (commands):
- Confirm pods, HPA:  
  `kubectl -n autoscale-demo get pods,deploy,hpa -w`

- Check HPA decisions:  
  `kubectl -n autoscale-demo describe hpa demo-app-hpa`

- Check VPA recommendations:  
  `kubectl -n autoscale-demo get vpa`  
  `kubectl -n autoscale-demo describe vpa demo-app-vpa`

- Generate load:  
  `kubectl -n autoscale-demo apply -f load-generator.yaml`  
  `watch kubectl -n autoscale-demo get pods -w`  
  HPA should scale pods up as CPU average rises (ensure metrics-server is Ready)

Cluster Autoscaler demo notes (Minikube)
- Real Cluster Autoscaler requires cloud provider APIs to add/remove VM nodes automatically.
- On Minikube we simulate the node-supply change manually:
  - Start Minikube with 1 node, then add a node:
    - If cluster started with single node, you can restart minikube with more nodes:
      minikube stop
      minikube start --nodes=3
    - Or use `minikube node add` if supported in your minikube version.
  - Watch pending pods: if HPA scales beyond capacity you will see Pending pods due to insufficient resources.
  - Add nodes (above) to provide capacity; scheduler will place the pending pods and HPA scaling will complete.
  - To simulate scale-down, remove nodes (careful): `minikube node delete` or restart with fewer nodes.

Why PodDisruptionBudget (PDB) matters
- VPA Recreate/InPlaceOrRecreate modes evict pods to apply new requests. PDBs limit how many pods can be evicted at once.
- Without a PDB, VPA could evict many replicas and cause downtime. With a PDB you ensure at least N pods remain available while VPA performs controlled evictions.
- Example PDB (minAvailable:1) protects availability during automated VPA updates:
  `kubectl apply -f demo-app-pdb.yaml`

Cleanup
- kubectl delete -f load-generator.yaml
- kubectl delete -f vpa-object.yaml
- kubectl delete -f hpa.yaml
- kubectl delete -f demo-app-deployment.yaml
- kubectl delete -f namespace.yaml

Final advice (concise)
- Start VPA in Off to gather data. Use PDBs, LimitRange, and maxAllowed to bound changes. Automate carefully: prefer CI/CD + canary for broad changes; enable Auto only for workloads you’ve validated
