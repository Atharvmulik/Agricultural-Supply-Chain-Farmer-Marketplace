# routes.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import models

app = Flask(__name__)
CORS(app)


# -------------------------------
# Registration
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    success, msg = models.create_user(data['name'], data['email'], data['password'], data['role'])
    if success:
        return jsonify({"status":"success","message":msg})
    return jsonify({"status":"error","message":msg}), 400


# -------------------------------
# Login
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = models.get_user_by_email(data['email'])
    if user and models.check_user_password(user, data['password']):
        return jsonify({"status":"success","message":"Login successful","user":user})
    return jsonify({"status":"error","message":"Invalid credentials"}), 401


# -------------------------------
# Farmer: Add Crop
# -------------------------------
@app.route('/add_crop', methods=['POST'])
def add_crop():
    data = request.json
    models.add_crop(data['farmer_id'], data['name'], data['price'], data['quantity'])
    return jsonify({"status":"success","message":"Crop added successfully"})


# -------------------------------
# Farmer: View Crops
# -------------------------------
@app.route('/farmer_crops/<int:farmer_id>', methods=['GET'])
def farmer_crops(farmer_id):
    crops = models.get_crops_by_farmer(farmer_id)
    return jsonify(crops)


# -------------------------------
# Buyer: View All Crops
# -------------------------------
@app.route('/crops', methods=['GET'])
def all_crops():
    crops = models.get_all_crops()
    return jsonify(crops)


# -------------------------------
# Buyer: Place Order
# -------------------------------
@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    success, msg = models.place_order(data['buyer_id'], data['crop_id'], data['quantity'])
    if success:
        return jsonify({"status":"success","message":msg})
    return jsonify({"status":"error","message":msg}), 400


# -------------------------------
# Buyer: View Orders
# -------------------------------
@app.route('/orders/<int:buyer_id>', methods=['GET'])
def buyer_orders(buyer_id):
    orders = models.get_orders_by_buyer(buyer_id)
    return jsonify(orders)


if __name__ == '__main__':
    app.run(debug=True)
