# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import models
import traceback

app = Flask(__name__)
app.secret_key = 'agrilink_secret_key_2025'
CORS(app)

# -------------------------------
# HTML Page Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/farmer_dashboard.html')
def farmer_dashboard():
    return render_template('farmer_dashboard.html')

@app.route('/buyer_dashboard.html')
def buyer_dashboard():
    return render_template('buyer_dashboard.html')

# -------------------------------
# API Routes - Authentication
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    try:
        if not request.is_json:
            return jsonify({"status":"error","message":"Request must be JSON"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"status":"error","message":"No JSON data received"}), 400
            
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not all([name, email, password, role]):
            return jsonify({"status":"error","message":"All fields are required"}), 400

        success, message, user = models.create_user(name, email, password, role)
        
        if success:
            return jsonify({
                "status":"success",
                "message": message,
                "user": user
            }), 200
        else:
            return jsonify({"status":"error","message": message}), 400
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message": "Internal server error"}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({"status":"error","message":"Email and password required"}), 400

        user = models.get_user_by_email(email)
        
        if user and models.check_user_password(user, password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            
            return jsonify({
                "status":"success",
                "message":"Login successful",
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "role": user['role']
                }
            }), 200
        
        return jsonify({"status":"error","message":"Invalid email or password"}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status":"success","message":"Logged out successfully"}), 200


@app.route('/user_session', methods=['GET'])
def get_user_session():
    try:
        if 'user_id' in session:
            return jsonify({
                "id": session['user_id'],
                "name": session['user_name'],
                "role": session['role']
            }), 200
        return jsonify({"error": "No active session"}), 401
    except Exception as e:
        print(f"Session error: {str(e)}")
        return jsonify({"error": "Session error"}), 500


# -------------------------------
# API Routes - Crops
# -------------------------------
@app.route('/add_crop', methods=['POST'])
def add_crop():
    try:
        data = request.json
        print(f"Received crop data: {data}")
        
        farmer_id = data.get('farmer_id')
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')
        description = data.get('description', '')
        category = data.get('category', 'Other')
        image_url = data.get('image_url', '')

        if not all([farmer_id, name, price, quantity]):
            return jsonify({"status":"error","message":"Missing required fields"}), 400

        success, message = models.add_crop(farmer_id, name, price, quantity, description, category, image_url)
        
        if success:
            return jsonify({"status":"success","message":message}), 200
        else:
            return jsonify({"status":"error","message":message}), 400
            
    except Exception as e:
        print(f"Add crop error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


@app.route('/farmer_crops/<int:farmer_id>', methods=['GET'])
def farmer_crops(farmer_id):
    try:
        print(f"Fetching crops for farmer ID: {farmer_id}")
        crops = models.get_crops_by_farmer(farmer_id)
        print(f"Found {len(crops)} crops")
        return jsonify(crops), 200
    except Exception as e:
        print(f"Farmer crops error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


@app.route('/crops', methods=['GET'])
def all_crops():
    try:
        print("Fetching all crops...")
        crops = models.get_all_crops()
        print(f"Returning {len(crops)} crops")
        return jsonify(crops), 200
    except Exception as e:
        print(f"All crops error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


# -------------------------------
# API Routes - Orders
# -------------------------------
@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        data = request.json
        print(f"Placing order: {data}")
        
        buyer_id = data.get('buyer_id')
        crop_id = data.get('crop_id')
        quantity = data.get('quantity')

        if not all([buyer_id, crop_id, quantity]):
            return jsonify({"status":"error","message":"Missing required fields"}), 400

        success, message = models.place_order(buyer_id, crop_id, quantity)
        
        if success:
            return jsonify({"status":"success","message":message}), 200
        else:
            return jsonify({"status":"error","message":message}), 400
            
    except Exception as e:
        print(f"Place order error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


@app.route('/orders/<int:buyer_id>', methods=['GET'])
def buyer_orders(buyer_id):
    try:
        print(f"Fetching orders for buyer ID: {buyer_id}")
        orders = models.get_orders_by_buyer(buyer_id)
        print(f"Found {len(orders)} orders")
        return jsonify(orders), 200
    except Exception as e:
        print(f"Buyer orders error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = models.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        print(f"Stats error: {str(e)}")
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500

# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)