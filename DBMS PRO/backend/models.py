# models.py
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    """Create a new database connection"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="aTHARV@123",
            database="agrilinkdb",
            autocommit=False
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

def convert_decimals(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

# -------------------------------
# User Functions
# -------------------------------
def create_user(name, email, password, role):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        hashed_password = generate_password_hash(password)
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        if cursor.fetchone():
            return False, "Email already exists", None

        sql = "INSERT INTO Users (name,email,password,role) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (name, email, hashed_password, role))
        connection.commit()
        
        cursor.execute("SELECT id, name, email, role FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user:
            user = convert_decimals(user)
            return True, "User registered successfully", user
        return False, "Failed to retrieve user after creation", None
    except Exception as e:
        connection.rollback()
        print(f"Error creating user: {e}")
        return False, str(e), None
    finally:
        cursor.close()
        connection.close()

def get_user_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        return convert_decimals(user) if user else None
    finally:
        cursor.close()
        connection.close()

def check_user_password(user, password):
    return check_password_hash(user['password'], password)

def get_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as count FROM Users WHERE role='farmer'")
        farmers_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Users WHERE role='buyer'")
        buyers_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Crops")
        crops_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Orders")
        orders_count = cursor.fetchone()['count']
        
        return {
            'farmers': farmers_count,
            'buyers': buyers_count,
            'crops': crops_count,
            'orders': orders_count
        }
    finally:
        cursor.close()
        connection.close()

# -------------------------------
# Crop Functions
# -------------------------------
def add_crop(farmer_id, name, price, quantity, description='', category='Other', image_url=''):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if not image_url:
            image_url = 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6'
        
        sql = "INSERT INTO Crops (farmer_id,name,price,quantity,description,category,image_url) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (farmer_id, name, price, quantity, description, category, image_url))
        connection.commit()
        print(f"Crop added: {name}, Price: {price}, Quantity: {quantity}")
        return True, "Crop added successfully"
    except Exception as e:
        connection.rollback()
        print(f"Error adding crop: {e}")
        return False, str(e)
    finally:
        cursor.close()
        connection.close()

def get_crops_by_farmer(farmer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Crops WHERE farmer_id=%s ORDER BY created_at DESC", (farmer_id,))
        crops = cursor.fetchall()
        return convert_decimals(crops)
    finally:
        cursor.close()
        connection.close()

def get_all_crops():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                Crops.id,
                Crops.farmer_id,
                Crops.name,
                Crops.price,
                Crops.quantity,
                Crops.description,
                Crops.category,
                Crops.image_url,
                Crops.created_at,
                Users.name AS farmer_name
            FROM Crops 
            JOIN Users ON Crops.farmer_id = Users.id
            ORDER BY Crops.created_at DESC
        """
        cursor.execute(sql)
        crops = cursor.fetchall()
        crops = convert_decimals(crops)
        print(f"Fetched {len(crops)} crops from database")
        for crop in crops:
            print(f"Crop: {crop['name']}, Quantity: {crop['quantity']}, Price: {crop['price']}")
        return crops
    except Exception as e:
        print(f"Error fetching crops: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_crop(crop_id, name, price, quantity, description, category):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        sql = "UPDATE Crops SET name=%s, price=%s, quantity=%s, description=%s, category=%s WHERE id=%s"
        cursor.execute(sql, (name, price, quantity, description, category, crop_id))
        connection.commit()
        return True, "Crop updated successfully"
    except Exception as e:
        connection.rollback()
        print(f"Error updating crop: {e}")
        return False, str(e)
    finally:
        cursor.close()
        connection.close()

def delete_crop(crop_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM Crops WHERE id=%s", (crop_id,))
        connection.commit()
        return True, "Crop deleted successfully"
    except Exception as e:
        connection.rollback()
        print(f"Error deleting crop: {e}")
        return False, str(e)
    finally:
        cursor.close()
        connection.close()

# -------------------------------
# Order Functions
# -------------------------------
def place_order(buyer_id, crop_id, quantity):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT price, quantity FROM Crops WHERE id=%s", (crop_id,))
        crop = cursor.fetchone()
        if not crop:
            return False, "Crop not found"
        
        crop = convert_decimals(crop)
        
        if quantity > crop['quantity']:
            return False, f"Insufficient crop quantity. Available: {crop['quantity']}kg"

        total_price = quantity * float(crop['price'])

        cursor.execute("INSERT INTO Orders (buyer_id,crop_id,quantity,total_price) VALUES (%s,%s,%s,%s)",
                       (buyer_id, crop_id, quantity, total_price))
        
        new_quantity = crop['quantity'] - quantity
        cursor.execute("UPDATE Crops SET quantity=%s WHERE id=%s", (new_quantity, crop_id))
        
        connection.commit()
        print(f"Order placed: Crop ID {crop_id}, Quantity: {quantity}, Total: {total_price}")
        return True, "Order placed successfully"
    except Exception as e:
        connection.rollback()
        print(f"Error placing order: {e}")
        return False, str(e)
    finally:
        cursor.close()
        connection.close()

def get_orders_by_buyer(buyer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                Orders.id,
                Orders.buyer_id,
                Orders.crop_id,
                Orders.quantity,
                Orders.total_price,
                Orders.status,
                Orders.created_at,
                Crops.name AS crop_name, 
                Crops.image_url, 
                Users.name AS farmer_name
            FROM Orders
            JOIN Crops ON Orders.crop_id = Crops.id
            JOIN Users ON Crops.farmer_id = Users.id
            WHERE Orders.buyer_id=%s
            ORDER BY Orders.created_at DESC
        """, (buyer_id,))
        orders = cursor.fetchall()
        return convert_decimals(orders)
    except Exception as e:
        print(f"Error fetching buyer orders: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_orders_by_farmer(farmer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                Orders.id,
                Orders.buyer_id,
                Orders.crop_id,
                Orders.quantity,
                Orders.total_price,
                Orders.status,
                Orders.created_at,
                Crops.name AS crop_name, 
                Users.name AS buyer_name
            FROM Orders
            JOIN Crops ON Orders.crop_id = Crops.id
            JOIN Users ON Orders.buyer_id = Users.id
            WHERE Crops.farmer_id=%s
            ORDER BY Orders.created_at DESC
        """, (farmer_id,))
        orders = cursor.fetchall()
        return convert_decimals(orders)
    except Exception as e:
        print(f"Error fetching farmer orders: {e}")
        return []
    finally:
        cursor.close()
        connection.close()