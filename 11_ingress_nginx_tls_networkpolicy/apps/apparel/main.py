from flask import Flask, jsonify

app = Flask(__name__)

PRODUCTS = [
    {"id": 1, "name": "Classic White Shirt", "price": 29.99, "category": "shirts"},
    {"id": 2, "name": "Slim Fit Jeans",      "price": 49.99, "category": "pants"},
    {"id": 3, "name": "Summer Dress",         "price": 39.99, "category": "dresses"},
]

@app.route("/apparel")
def list_apparel():
    return jsonify(service="apparel-api", products=PRODUCTS)

@app.route("/apparel/<int:product_id>")
def get_apparel(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify(error="not found"), 404
    return jsonify(service="apparel-api", product=product)

@app.route("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
