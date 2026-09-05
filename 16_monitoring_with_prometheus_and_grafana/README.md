# Prometheus & Grafana Monitoring Demo

## Project Structure
```
16_monitoring_with_prometheus_and_grafana/
├── app/
│   ├── main.py              # Flask app with custom metrics
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 01-sample-app.yaml   # Sample app deployment
│   ├── 02-prometheus.yaml   # Prometheus + RBAC + config + alert rules
│   ├── 03-alertmanager.yaml # Alertmanager + Slack config
│   ├── 04-node-exporter.yaml
│   └── 05-grafana.yaml      # Grafana + dashboards
├── prometheus/
│   ├── prometheus.yaml      # standalone reference config
│   └── alert-rules.yaml
├── alertmanager/
│   └── alertmanager.yaml    # standalone reference config
└── grafana/
    └── provisioning/
        ├── datasources/
        └── dashboards/
```

## Prerequisites
- WSL2 with minikube installed
- Docker installed inside WSL2
- kubectl configured

## Step 1 — Configure Slack Webhook
Before deploying, replace the placeholders in `k8s/03-alertmanager.yaml`:
- `<YOUR_SLACK_WEBHOOK_URL>` → your Slack incoming webhook URL
  - Go to: https://api.slack.com/apps → Create App → Incoming Webhooks
- `<YOUR_SLACK_CHANNEL>` → e.g. `#alerts`

## Step 2 — Start Minikube
```bash
minikube start --driver=docker
```

## Step 3 — Build Sample App Image inside Minikube
```bash
# point docker to minikube's docker daemon
eval $(minikube docker-env)

# build the image
docker build -t sample-app:latest ./app/
```

## Step 4 — Deploy Everything
```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-sample-app.yaml
kubectl apply -f k8s/02-prometheus.yaml
kubectl apply -f k8s/03-alertmanager.yaml
kubectl apply -f k8s/04-node-exporter.yaml
kubectl apply -f k8s/05-grafana.yaml
```

## Step 5 — Verify All Pods are Running
```bash
kubectl get pods -n monitoring
```

## Step 6 — Access UIs in Browser

### On WSL2, get minikube IP:
```bash
minikube ip
# example output: 192.168.49.2
```

| Service       | URL                          | Credentials       |
|---------------|------------------------------|-------------------|
| Prometheus    | http://<minikube-ip>:30090   | -                 |
| Alertmanager  | http://<minikube-ip>:30093   | -                 |
| Grafana       | http://<minikube-ip>:30030   | admin / admin123  |

> On WSL2 if minikube IP is not reachable from browser, run:
> ```bash
> minikube tunnel
> # then use http://localhost:30090, http://localhost:30030
> ```

## Step 7 — Generate Traffic to Sample App
```bash
# get sample-app pod name
kubectl get pods -n monitoring

# exec into it and generate traffic
kubectl run -n monitoring curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  sh -c 'while true; do curl -s http://sample-app:5000/; curl -s http://sample-app:5000/order; sleep 1; done'
```

## Step 8 — Verify in Prometheus
- Open Prometheus → http://<minikube-ip>:30090
- Go to Status → Targets — you should see `sample-app`, `node-exporter`, `prometheus` all UP
- Try queries:
  ```
  app_requests_total
  app_active_users
  rate(app_requests_total[5m])
  histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[5m]))
  ```

## Step 9 — View Grafana Dashboard
- Open Grafana → http://<minikube-ip>:30030
- Login: admin / admin123
- Go to Dashboards → "Sample App Dashboard"
- You'll see: requests/sec, p95 latency, active users, revenue, orders, error rate

## Custom Metrics Exposed by Sample App
| Metric | Type | Description |
|--------|------|-------------|
| `app_requests_total` | Counter | Total HTTP requests by method/endpoint/status |
| `app_request_latency_seconds` | Histogram | Request latency per endpoint |
| `app_active_users` | Gauge | Simulated active user count |
| `app_orders_total` | Counter | Orders by status (success/failed/pending) |
| `app_revenue_dollars` | Gauge | Cumulative revenue |

## Alert Rules Configured
| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | 5xx rate > 0.1 req/s for 1m | critical |
| HighRequestLatency | p95 latency > 400ms for 2m | warning |
| NoActiveUsers | active users < 5 for 1m | warning |
| HighCPUUsage | CPU > 80% for 2m | warning |
| HighMemoryUsage | Memory > 85% for 2m | critical |

## Teardown
```bash
kubectl delete namespace monitoring
```
