# Top 10 Kubernetes App Failures — Brief Explanations

This directory contains 10 common failure scenarios encountered when deploying applications on Kubernetes. Each folder demonstrates a specific misconfiguration or runtime issue.

Steps to emulate this session - 
1. Clone the repo and go into the directory 06_real-time_top10_app_deployment_erroneous_scenarios
2. Create docker image with command `docker build -t demo-app:1.0 .`
3. Start the minikube `minikube start`
4. If you have setup kubernetes cluster through minikube then open the another terminal and initiate the tunnel `minikube tunnel`. Ensure it is running when it is needed.
5. Now go into each erroneous sub directory and apply the existing manifest file as illustrated in the video
6. Before going into the next erroneous sub directory, please delete the applied manifest as in  
`kubectl get deployment`  
`kubectl delete deployment <deployment_name>`  
`kubectl get svc`  
`kubectl delete service <service_name>`
---    

1. Deployment Pod Label Mismatch  
   Pods are created with labels that do not match the Deployment selector, so the Deployment cannot manage or scale the intended pods.

2. Service Pod Selector Mismatch  
   Service selectors do not match pod labels, so the Service has no endpoints and traffic is not routed to the pods.

3. Wrong Image Tag  
   The Deployment references a non-existent or incorrect image tag, causing image pull failures or runtime crashes.

4. Readiness Probe Misconfigured  
   Incorrect readiness settings make pods report as not ready, preventing them from receiving traffic even when containers run.

5. Resource Limits Too Low  
   Requests/limits are set too low, causing CPU throttling or OOMKilled terminations and unstable application behavior.

6. Container Port Mismatch  
   The containerPort and the Service targetPort do not align, resulting in unreachable application endpoints.

7. Missing ConfigMap  
   The application expects configuration from a ConfigMap that is absent or misnamed, leading to startup errors or incorrect behavior.

8. Missing Secret  
   Required secrets (credentials or keys) are not provided or mounted, causing authentication failures or crashes.

9. Node Selector / Affinity Issue  
   Pod scheduling fails (pods remain Pending) because node selectors or affinity rules do not match any available nodes.

10. Service Type Misconfiguration  
   Using the wrong Service type (ClusterIP/NodePort/LoadBalancer) or incorrect ports leads to inaccessible services or unintended exposure.

---
Summary: Each scenario highlights a focused, real-world misconfiguration. Use these examples to practice detection and remediation of deployment and networking
