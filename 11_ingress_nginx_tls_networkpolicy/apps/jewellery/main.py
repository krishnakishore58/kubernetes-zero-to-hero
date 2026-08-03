from flask import Flask, jsonify

app = Flask(__name__)

PRODUCTS = [
    {"id": 1, "name": "Gold Necklace",    "price": 299.99, "category": "necklaces"},
    {"id": 2, "name": "Diamond Ring",     "price": 999.99, "category": "rings"},
    {"id": 3, "name": "Pearl Earrings",   "price": 149.99, "category": "earrings"},
]

@app.route("/jewellery")
def list_jewellery():
    return jsonify(service="jewellery-api", products=PRODUCTS)

@app.route("/jewellery/<int:product_id>")
def get_jewellery(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify(error="not found"), 404
    return jsonify(service="jewellery-api", product=product)

@app.route("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
