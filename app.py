from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "pandesal_express_secret_key"

# Master List of 20 Bread Products
BASE_PRODUCTS = [
    {"id": 1, "name": "Classic Pandesal (10 pcs)", "price": 25.0, "desc": "Traditional freshly baked Filipino breakfast roll."},
    {"id": 2, "name": "Malunggay Pandesal (10 pcs)", "price": 30.0, "desc": "Nutritious pandesal infused with fresh malunggay leaves."},
    {"id": 3, "name": "Cheese Bread (6 pcs)", "price": 45.0, "desc": "Soft bread rolls topped with sweet grated cheese."},
    {"id": 4, "name": "Spanish Bread (6 pcs)", "price": 50.0, "desc": "Rolled bread filled with sweet butter and breadcrumb filling."},
    {"id": 5, "name": "Ube Pandesal w/ Cheese (6 pcs)", "price": 65.0, "desc": "Purple yam flavored pandesal stuffed with cheese."},
    {"id": 6, "name": "Pan de Coco (5 pcs)", "price": 40.0, "desc": "Sweet bread buns stuffed with grated sweetened coconut."},
    {"id": 7, "name": "Special Monay (2 pcs)", "price": 35.0, "desc": "Dense and heavy sweet bread roll."},
    {"id": 8, "name": "Classic Ensaymada (2 pcs)", "price": 50.0, "desc": "Brioche bun topped with butter, sugar, and cheese."},
    {"id": 9, "name": "Ube Ensaymada (2 pcs)", "price": 60.0, "desc": "Ube-infused ensaymada with cheese topping."},
    {"id": 10, "name": "Pianono Roll (1 pc)", "price": 40.0, "desc": "Soft sponge cake roll filled with sweet margarine and sugar."},
    {"id": 11, "name": "Kalihim / Bread Pudding (5 pcs)", "price": 35.0, "desc": "Traditional bread stuffed with bright red pudding fill."},
    {"id": 12, "name": "Kababayan (6 pcs)", "price": 30.0, "desc": "Gong-shaped sweet muffin bread."},
    {"id": 13, "name": "Biscocho Toast (1 pack)", "price": 45.0, "desc": "Crunchy double-baked buttered toast."},
    {"id": 14, "name": "Star Bread / Putok (4 pcs)", "price": 35.0, "desc": "Hard-crusted sweet roll with a star cut top."},
    {"id": 15, "name": "Choco Roll (4 pcs)", "price": 45.0, "desc": "Bread roll filled with rich chocolate fudge."},
    {"id": 16, "name": "Garlic Butter Toast (1 pack)", "price": 50.0, "desc": "Crispy toast glazed with garlic and butter."},
    {"id": 17, "name": "Premium Tasty Loaf (1 loaf)", "price": 65.0, "desc": "Soft sliced white bread loaf."},
    {"id": 18, "name": "Whole Wheat Loaf (1 loaf)", "price": 75.0, "desc": "Healthy whole grain sliced bread."},
    {"id": 19, "name": "Cinnamon Sugar Roll (4 pcs)", "price": 55.0, "desc": "Soft rolls sprinkled with cinnamon powder and sugar."},
    {"id": 20, "name": "Custard Cream Bread (4 pcs)", "price": 50.0, "desc": "Soft bun filled with smooth custard cream."}
]

# 5 Nearby Vendors
VENDORS = [
    {"id": 1, "name": "Pan de Concepcion", "distanceKm": 0.5, "deliveryFee": 20.0, "products": BASE_PRODUCTS},
    {"id": 2, "name": "Marikina Heights Bakery", "distanceKm": 1.2, "deliveryFee": 30.0, "products": BASE_PRODUCTS},
    {"id": 3, "name": "Kamuning Bakery - Extension", "distanceKm": 2.4, "deliveryFee": 45.0, "products": BASE_PRODUCTS},
    {"id": 4, "name": "San Roque Hot Pandesal", "distanceKm": 3.8, "deliveryFee": 55.0, "products": BASE_PRODUCTS},
    {"id": 5, "name": "Riverbanks Morning Crust", "distanceKm": 5.1, "deliveryFee": 70.0, "products": BASE_PRODUCTS}
]

# Customer Order Log Database (10 Initial Pre-orders)
CUSTOMER_LOGS = [
    {"order_id": 1001, "customer_name": "Maria Santos", "address": "Block 5 Lot 12, Concepcion Uno", "vendor_name": "Pan de Concepcion", "items": "Classic Pandesal (x2), Spanish Bread (x1)", "total_amount": 100.0, "delivery_time": "06:30 AM", "status": "Delivered"},
    {"order_id": 1002, "customer_name": "Jose Rizal", "address": "#45 Calumpang St.", "vendor_name": "Marikina Heights Bakery", "items": "Ube Pandesal w/ Cheese (x2)", "total_amount": 160.0, "delivery_time": "06:45 AM", "status": "Delivered"},
    {"order_id": 1003, "customer_name": "Andres Bonifacio", "address": "123 Sto. Niño Ave.", "vendor_name": "Pan de Concepcion", "items": "Classic Ensaymada (x3)", "total_amount": 170.0, "delivery_time": "07:00 AM", "status": "Delivered"},
    {"order_id": 1004, "customer_name": "Clara Recto", "address": "78 Malanday Main Road", "vendor_name": "Kamuning Bakery - Extension", "items": "Malunggay Pandesal (x2), Pan de Coco (x1)", "total_amount": 145.0, "delivery_time": "07:15 AM", "status": "Delivered"},
    {"order_id": 1005, "customer_name": "Emilio Aguinaldo", "address": "#12 San Roque St.", "vendor_name": "San Roque Hot Pandesal", "items": "Special Monay (x2), Premium Tasty Loaf (x1)", "total_amount": 180.0, "delivery_time": "07:30 AM", "status": "Delivered"},
    {"order_id": 1006, "customer_name": "Apolinario Mabini", "address": "Phase 2 Barangka", "vendor_name": "Riverbanks Morning Crust", "items": "Whole Wheat Loaf (x1), Cheese Bread (x1)", "total_amount": 190.0, "delivery_time": "07:45 AM", "status": "Delivered"},
    {"order_id": 1007, "customer_name": "Gabriela Silang", "address": "56 Industrial Valley", "vendor_name": "Pan de Concepcion", "items": "Classic Pandesal (x4)", "total_amount": 120.0, "delivery_time": "08:00 AM", "status": "Delivered"},
    {"order_id": 1008, "customer_name": "Juan Luna", "address": "Unit 4A Jesus Dela Peña", "vendor_name": "Marikina Heights Bakery", "items": "Garlic Butter Toast (x2)", "total_amount": 130.0, "delivery_time": "08:15 AM", "status": "Delivered"},
    {"order_id": 1009, "customer_name": "Melchora Aquino", "address": "89 Nangka Rd.", "vendor_name": "Kamuning Bakery - Extension", "items": "Custard Cream Bread (x2)", "total_amount": 145.0, "delivery_time": "08:30 AM", "status": "Delivered"},
    {"order_id": 1010, "customer_name": "Gregorio del Pilar", "address": "15 Fortune Vista", "vendor_name": "San Roque Hot Pandesal", "items": "Kababayan (x3), Biscocho Toast (x1)", "total_amount": 190.0, "delivery_time": "08:45 AM", "status": "Delivered"}
]

VENDORS.sort(key=lambda x: x["distanceKm"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    session['user'] = {"name": name, "email": email}
    return jsonify({"success": True, "user": session['user']})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user' in session:
        return jsonify({"logged_in": True, "user": session['user']})
    return jsonify({"logged_in": False})

@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    return jsonify(VENDORS)

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json(force=True)
    vendor = next((v for v in VENDORS if v["id"] == data.get("vendor_id")), None)

    if not vendor:
        return jsonify({"success": False, "message": "Vendor not found"}), 400

    items_str = ", ".join([f"{item['name']} (x{item['qty']})" for item in data.get("cart", [])])
    
    new_order = {
        "order_id": 1000 + len(CUSTOMER_LOGS) + 1,
        "customer_name": data.get("name"),
        "address": data.get("address"),
        "vendor_name": vendor["name"],
        "items": items_str,
        "total_amount": float(data.get("total")),
        "delivery_time": data.get("time"),
        "status": "Confirmed"
    }

    CUSTOMER_LOGS.insert(0, new_order)
    return jsonify({"success": True, "order": new_order})

@app.route('/api/customer-logs', methods=['GET'])
def get_customer_logs():
    return jsonify(CUSTOMER_LOGS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)