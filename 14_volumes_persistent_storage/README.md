Demo C — Dynamic PVC demo (minikube / local-path)

Purpose
- Show dynamic provisioning using a StorageClass + PVC on a local/demo cluster (minikube).
- Verify data persists across Pod restarts using the same PVC.

Files in this folder
- install-local-path.yaml  (optional) — deploys a simple local-path provisioner for dynamic provisioning
- storageclass-local-path.yaml — StorageClass that uses the local-path provisioner
- pvc-demo.yaml — a 1Gi PersistentVolumeClaim using the StorageClass
- pod-using-pvc.yaml — a Pod that mounts the claim

Two ways to get a provisioner on minikube
A) Recommended (fast): enable minikube's storage addon (built-in provisioner)
   minikube addons enable storage-provisioner
   - If you use this, omit applying install-local-path.yaml and use storageClassName "standard" or omit storageClassName in pvc-demo.yaml.

B) Alternate (manifest): apply the included local-path provisioner manifest
   kubectl apply -f install-local-path.yaml
   This will create a provisioner named "rancher.io/local-path".

Quick apply (if using the included local-path manifest):
```bash
for node in $(kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'); do   docker exec -it "$node" sh -c 'mkdir -p /opt/local-path-provisioner && chown -R 1000:1000 /opt/local-path-provisioner'; done

kubectl apply -f install-local-path.yaml
kubectl apply -f storageclass-local-path.yaml
kubectl apply -f pvc-demo.yaml
kubectl apply -f pod-using-pvc.yaml
```

Verify and test persistence
1) Confirm StorageClass exists and (if using manifest) is the expected one:
```bash
kubectl get sc
kubectl describe sc local-path
```
2) Ensure the PVC binds:
```bash
kubectl get pvc demo-pvc
# wait until STATUS == Bound
kubectl describe pvc demo-pvc
```
3) Write data into the mounted volume:
```bash
kubectl exec -it pod-using-demo-pvc -- sh -c "echo persisted > /data/persist.txt && ls -l /data"
```
4) Delete the Pod and recreate it to demonstrate persistence:
```bash
kubectl delete pod pod-using-demo-pvc
kubectl apply -f pod-using-pvc.yaml
# wait for the new pod to be Running
kubectl exec -it pod-using-demo-pvc -- cat /data/persist.txt
```
Expected: the content "persisted" is still present.

Troubleshooting
- If PVC stays Pending: no provisioner matching the PVC's storageClassName exists. Check `kubectl get sc` and ensure you either enabled minikube's addon or applied install-local-path.yaml.
- If permission errors writing files: check the provisioner config and hostPath directory permissions (hostPath provisioners create directories under the host path).
- If you prefer minikube builtin: run `minikube addons enable storage-provisioner` and change `storageClassName: "local-path"` in `pvc-demo.yaml` to `standard` or remove the storageClassName to use default.

Notes
- These manifests are intentionally minimal for demo use only. Do not use hostPath-style local provisioners in production without understanding topology, redundancy and backup.
