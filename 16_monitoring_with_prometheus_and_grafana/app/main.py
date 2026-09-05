from flask import Flask
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time
import threading

app = Flask(__name__)

# Custom metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency', ['endpoint'])
ACTIVE_USERS = Gauge('app_active_users', 'Number of active users')
ORDER_COUNT = Counter('app_orders_total', 'Total orders placed', ['status'])
REVENUE = Gauge('app_revenue_dollars', 'Total revenue in dollars')

def simulate_background_metrics():
    revenue = 0
    while True:
        ACTIVE_USERS.set(random.randint(10, 500))
        status = random.choice(['success', 'failed', 'pending'])
        ORDER_COUNT.labels(status=status).inc()
        if status == 'success':
            revenue += random.uniform(10, 500)
            REVENUE.set(round(revenue, 2))
        time.sleep(5)

@app.route('/')
def home():
    start = time.time()
    time.sleep(random.uniform(0.01, 0.3))
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    return 'Sample App is running!'

@app.route('/order')
def order():
    start = time.time()
    time.sleep(random.uniform(0.05, 0.5))
    status = random.choice(['200', '500'])
    REQUEST_COUNT.labels(method='GET', endpoint='/order', status=status).inc()
    REQUEST_LATENCY.labels(endpoint='/order').observe(time.time() - start)
    return ('Order placed!', int(status))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    t = threading.Thread(target=simulate_background_metrics, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
