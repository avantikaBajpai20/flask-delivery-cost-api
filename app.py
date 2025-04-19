from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

# Stock data at each center
stock = {
    'C1': {'A': 3, 'B': 2, 'C': 5},
    'C2': {'A': 2, 'B': 3, 'C': 2},
    'C3': {'A': 1, 'B': 1, 'C': 3}
}

# Distance between centers and L1
distances = {
    ('C1', 'C2'): 10, ('C2', 'C1'): 10,
    ('C1', 'C3'): 20, ('C3', 'C1'): 20,
    ('C2', 'C3'): 15, ('C3', 'C2'): 15,
    ('C1', 'L1'): 30,
    ('C2', 'L1'): 35,
    ('C3', 'L1'): 40
}

PRODUCT_WEIGHT = 0.5  # weight per unit

def calculate_min_cost(order):
    centers = ['C1', 'C2', 'C3']
    min_cost = float('inf')

    for start in centers:
        for path in permutations([c for c in centers if c != start]):
            route = [start] + list(path) + ['L1']
            collected = {prod: 0 for prod in order}
            cost = 0

            for i in range(len(route) - 1):
                src = route[i]
                dst = route[i + 1]

                if src in stock:
                    for prod in order:
                        needed = order[prod] - collected[prod]
                        available = stock[src].get(prod, 0)
                        collected[prod] += min(needed, available)

                # Current total weight of collected items
                total_weight = sum(collected[prod] for prod in collected) * PRODUCT_WEIGHT

                # Get the distance or assume a very high value if not found
                dist = distances.get((src, dst), 1e6)

                # Increment cost
                cost += total_weight * dist

            # Check if all products have been collected
            if all(collected[p] >= order[p] for p in order):
                min_cost = min(min_cost, cost)

    return min_cost if min_cost != float('inf') else -1

@app.route('/')
def home():
    return "✅ API is up and running!"

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()
    order = data.get("order")

    if not order:
        return jsonify({"error": "No order provided"}), 400

    # Check if all products exist in stock
    available_products = set()
    for center in stock.values():
        available_products.update(center.keys())

    missing_products = [p for p in order if p not in available_products]
    if missing_products:
        return jsonify({"error": f"Products not available in any center: {', '.join(missing_products)}"}), 400

    result = calculate_min_cost(order)
    return jsonify({"minimum_cost": round(result, 2)})


if __name__ == '__main__':
    app.run(debug=True)
