# Kubernetes Demo: Deployment + ClusterIP + LoadBalancer + Debugging

Overview
This demo covers:
- YAML basics: apiVersion/kind/metadata/spec
- labels/selectors, container ports, probes, resources
- Deploy a Demo app and LoadBalancer services
- Reproduce and debug label mismatch, ImagePullBackOff, probe failures

Prereqs
- Docker
- kubectl configured to a cluster (minikube/EKS/GKE)
- (Optional) minikube for local testing

Build and push image
# 1. Build image locally
docker build -t demo-app:1.0 ./app
# 2. Start minikube cluster (if needed)
minikube start
# 3. Load image into minikube
minikube image load demo-app:1.0.   
minikube tunnel.   

Deploy to cluster:  
kubectl apply -f k8s/deployment.yaml  
kubectl apply -f k8s/service-loadbalancer.yaml

Verify:  
kubectl get pods -o wide  
kubectl get svc. 
kubectl get endpoints demo-app-loadbalancer.yaml

Useful commands:  
kubectl describe pod <pod> -n default  
kubectl logs -f deployment/demo-app.  
kubectl exec -it <pod> -- /bin/sh. 

Teardown:  
kubectl delete -f k8s/service-loadbalancer.yaml.  
kubectl delete -f k8s/deployment.yaml


