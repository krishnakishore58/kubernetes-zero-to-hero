# create namespace and apply resources
```bash
kubectl apply -f demo/00-namespace.yaml
kubectl apply -f demo/01-configmap.yaml
kubectl apply -f demo/02-secret.yaml
kubectl apply -f demo/03-deployment-uses-configmap-secret.yaml

# verify
kubectl -n demo-secrets get all
kubectl -n demo-secrets exec deploy/web-demo -- printenv | egrep '^DB_'
kubectl -n demo-secrets exec deploy/web-demo -- cat /usr/share/nginx/html/index.html
# port-forward to view in browser
kubectl -n demo-secrets port-forward deploy/web-demo 8080:80
# then open http://localhost:8080
```