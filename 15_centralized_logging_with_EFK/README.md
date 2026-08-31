# EFK demo (Kubernetes / minikube)

Quick demo to show logs flowing: Pod → Fluentd (DaemonSet) → Elasticsearch → Kibana.

## Prerequisites
- kubectl configured to target your cluster (minikube/kind).
- cluster has permissions to create the resources in these manifests.
- If running on minikube: you may need to run Fluentd as root and mount host log paths; see Troubleshooting.

## Apply manifests (order matters)
Run these commands from the repo root:
```bash
kubectl apply -f 15_centralized_logging_with_EFK/namespace.yaml
kubectl apply -f 15_centralized_logging_with_EFK/fluentd-rbac.yaml
kubectl apply -f 15_centralized_logging_with_EFK/elasticsearch-deployment.yaml
kubectl apply -f 15_centralized_logging_with_EFK/kibana-deployment.yaml
kubectl apply -f 15_centralized_logging_with_EFK/fluentd-configmap.yaml
kubectl apply -f 15_centralized_logging_with_EFK/fluentd-daemonset.yaml
kubectl apply -f 15_centralized_logging_with_EFK/demo-logger.yaml
```

## Verify cluster objects
```bash
kubectl -n efk get pods -o wide
kubectl -n efk get svc
# tail fluentd logs
kubectl -n efk logs -l app=fluentd --tail=200
```

## Port‑forward for local access
Open Elasticsearch and Kibana locally:
```bash
kubectl -n efk port-forward svc/elasticsearch 9200:9200 >/dev/null 2>&1 &
kubectl -n efk port-forward svc/kibana 5601:5601 >/dev/null 2>&1 &
# verify ES
curl -s http://127.0.0.1:9200/_cluster/health?pretty
curl -s http://127.0.0.1:9200/_cat/indices?v
```

## Create Kibana index pattern (UI)
1. Open http://127.0.0.1:5601
2. Stack Management → Index Patterns → Create index pattern
   - Index pattern: `kubernetes-logs*` or `logstash-*` (or exact prefix shown by `_cat/indices`)
   - Time field: select `@timestamp` if present (otherwise choose "I don’t want to use the time filter")
3. Go to Discover, set an appropriate time range, and search for `demo log` or `kubernetes.pod_name:logger`.
