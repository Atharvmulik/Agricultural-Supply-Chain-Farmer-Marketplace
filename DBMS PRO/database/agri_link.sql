-- ==========================================
-- DATABASE: AgriLinkDB
-- Agricultural Supply Chain & Farmer Marketplace
-- ==========================================

-- 1️⃣ Create the database
DROP DATABASE IF EXISTS AgriLinkDB;
CREATE DATABASE AgriLinkDB;
USE AgriLinkDB;

-- 2️⃣ Create Users table with enhanced fields
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer','buyer') NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    profile_image VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3️⃣ Create Crops table with enhanced fields
CREATE TABLE Crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    unit ENUM('kg','gram','ton','quintal','piece') DEFAULT 'kg',
    image_url VARCHAR(255),
    description TEXT,
    category VARCHAR(50),
    is_organic BOOLEAN DEFAULT FALSE,
    harvest_date DATE,
    expiry_date DATE,
    min_order_quantity INT DEFAULT 1,
    max_order_quantity INT,
    is_available BOOLEAN DEFAULT TRUE,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_ratings INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_category (category),
    INDEX idx_price (price),
    INDEX idx_created_at (created_at)
);

-- 4️⃣ Create Orders table with enhanced fields
CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    crop_id INT NOT NULL,
    farmer_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('Pending','Confirmed','Shipped','Delivered','Cancelled','Refunded') DEFAULT 'Pending',
    payment_status ENUM('Pending','Paid','Failed','Refunded') DEFAULT 'Pending',
    payment_method ENUM('Cash','UPI','Card','Net Banking') DEFAULT 'Cash',
    shipping_address TEXT,
    order_notes TEXT,
    expected_delivery_date DATE,
    delivered_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES Users(id),
    FOREIGN KEY (crop_id) REFERENCES Crops(id),
    FOREIGN KEY (farmer_id) REFERENCES Users(id),
    INDEX idx_buyer_id (buyer_id),
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 5️⃣ Create Reviews table
CREATE TABLE Reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    crop_id INT NOT NULL,
    buyer_id INT NOT NULL,
    farmer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (crop_id) REFERENCES Crops(id),
    FOREIGN KEY (buyer_id) REFERENCES Users(id),
    FOREIGN KEY (farmer_id) REFERENCES Users(id),
    UNIQUE KEY unique_order_review (order_id),
    INDEX idx_crop_id (crop_id),
    INDEX idx_farmer_id (farmer_id)
);

-- 6️⃣ Create Notifications table
CREATE TABLE Notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('order','system','promotion','alert') DEFAULT 'system',
    is_read BOOLEAN DEFAULT FALSE,
    related_id INT, -- Can be order_id, crop_id, etc.
    related_type VARCHAR(50), -- 'order', 'crop', 'system'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read)
);

-- 7️⃣ Create Wishlist table
CREATE TABLE Wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    crop_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES Users(id),
    FOREIGN KEY (crop_id) REFERENCES Crops(id),
    UNIQUE KEY unique_buyer_crop (buyer_id, crop_id)
);

-- Sample Users with enhanced data
INSERT INTO Users (name, email, password, role, phone, address, city, state, pincode) VALUES
('Ravi Kumar', 'ravi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj89OFmSQhSK', 'farmer', '9876543210', 'Farm House, Village Road', 'Chandigarh', 'Punjab', '160001'),
('Sita Sharma', 'sita@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj89OFmSQhSK', 'buyer', '9876543211', 'Apartment 101, Green City', 'Mumbai', 'Maharashtra', '400001'),
('Amit Patel', 'amit@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj89OFmSQhSK', 'farmer', '9876543212', 'Organic Farm, Highway Road', 'Ahmedabad', 'Gujarat', '380001'),
('Priya Singh', 'priya@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj89OFmSQhSK', 'buyer', '9876543213', 'House No. 45, MG Road', 'Delhi', 'Delhi', '110001');

-- Sample Crops with enhanced data
INSERT INTO Crops (farmer_id, name, price, quantity, unit, image_url, description, category, is_organic, harvest_date) VALUES
(1, 'Premium Wheat', 25.00, 500, 'kg', 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6', 'High-quality wheat from Punjab farms, rich in nutrients and perfect for making chapatis', 'Grains', TRUE, '2024-12-01'),
(1, 'Organic Basmati Rice', 55.00, 300, 'kg', 'https://images.unsplash.com/photo-1578916171728-46686eac8d58', 'Aromatic basmati rice, organically grown without pesticides. Long grain and fragrant.', 'Grains', TRUE, '2024-11-15'),
(1, 'Fresh Tomatoes', 40.00, 200, 'kg', 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea', 'Fresh red tomatoes, rich in lycopene and vitamins. Perfect for cooking and salads.', 'Vegetables', FALSE, '2024-12-10'),
(3, 'Alphonso Mangoes', 120.00, 100, 'kg', 'https://images.unsplash.com/photo-1553279768-865429fa0078', 'King of mangoes - sweet, juicy Alphonso mangoes from Gujarat. Limited seasonal availability.', 'Fruits', TRUE, '2024-05-01'),
(3, 'Organic Potatoes', 30.00, 400, 'kg', 'https://images.unsplash.com/photo-1518977676601-b53f82aba655', 'Fresh organic potatoes, perfect for all culinary uses. Grown without chemical fertilizers.', 'Vegetables', TRUE, '2024-12-05');

-- Sample Orders with enhanced data
INSERT INTO Orders (buyer_id, crop_id, farmer_id, quantity, unit_price, total_price, status, payment_status, shipping_address) VALUES
(2, 1, 1, 50, 25.00, 1250.00, 'Confirmed', 'Paid', 'Apartment 101, Green City, Mumbai, Maharashtra - 400001'),
(2, 3, 1, 30, 40.00, 1200.00, 'Pending', 'Pending', 'Apartment 101, Green City, Mumbai, Maharashtra - 400001'),
(4, 4, 3, 10, 120.00, 1200.00, 'Shipped', 'Paid', 'House No. 45, MG Road, Delhi - 110001'),
(4, 5, 3, 25, 30.00, 750.00, 'Delivered', 'Paid', 'House No. 45, MG Road, Delhi - 110001');

-- Sample Reviews
INSERT INTO Reviews (order_id, crop_id, buyer_id, farmer_id, rating, comment) VALUES
(4, 5, 4, 3, 5, 'Excellent quality potatoes! Very fresh and organic. Will order again.'),
(3, 4, 4, 3, 4, 'Mangoes were sweet and delicious. Packaging could be better.');

-- Sample Wishlist items
INSERT INTO Wishlist (buyer_id, crop_id) VALUES
(2, 4),
(2, 5),
(4, 1);

-- Sample Notifications
INSERT INTO Notifications (user_id, title, message, type, related_id, related_type) VALUES
(2, 'Order Confirmed', 'Your order for Premium Wheat has been confirmed by the farmer.', 'order', 1, 'order'),
(1, 'New Order Received', 'You have received a new order for 50kg of Premium Wheat.', 'order', 1, 'order'),
(4, 'Order Shipped', 'Your order for Alphonso Mangoes has been shipped.', 'order', 3, 'order');

-- Update crop ratings based on reviews
UPDATE Crops c SET 
rating = (
    SELECT AVG(r.rating) 
    FROM Reviews r 
    WHERE r.crop_id = c.id AND r.is_approved = TRUE
),
total_ratings = (
    SELECT COUNT(*) 
    FROM Reviews r 
    WHERE r.crop_id = c.id AND r.is_approved = TRUE
)
WHERE id IN (SELECT DISTINCT crop_id FROM Reviews);

-- Create useful views
CREATE VIEW Crop_Details AS
SELECT 
    c.*,
    u.name as farmer_name,
    u.city as farmer_city,
    u.state as farmer_state,
    COUNT(DISTINCT r.id) as review_count,
    AVG(r.rating) as average_rating
FROM Crops c
JOIN Users u ON c.farmer_id = u.id
LEFT JOIN Reviews r ON c.id = r.crop_id AND r.is_approved = TRUE
WHERE c.is_available = TRUE AND c.quantity > 0
GROUP BY c.id;

CREATE VIEW Order_Details AS
SELECT 
    o.*,
    c.name as crop_name,
    c.image_url as crop_image,
    buyer.name as buyer_name,
    farmer.name as farmer_name,
    farmer.phone as farmer_phone
FROM Orders o
JOIN Crops c ON o.crop_id = c.id
JOIN Users buyer ON o.buyer_id = buyer.id
JOIN Users farmer ON o.farmer_id = farmer.id;

-- Create stored procedure for placing orders
DELIMITER //
CREATE PROCEDURE PlaceOrder(
    IN p_buyer_id INT,
    IN p_crop_id INT,
    IN p_quantity INT
)
BEGIN
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_available_quantity INT;
    DECLARE v_farmer_id INT;
    DECLARE v_total_price DECIMAL(10,2);
    
    -- Get crop details
    SELECT price, quantity, farmer_id INTO v_price, v_available_quantity, v_farmer_id
    FROM Crops WHERE id = p_crop_id;
    
    -- Check availability
    IF v_available_quantity < p_quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient quantity available';
    END IF;
    
    -- Calculate total price
    SET v_total_price = v_price * p_quantity;
    
    -- Start transaction
    START TRANSACTION;
    
    -- Insert order
    INSERT INTO Orders (buyer_id, crop_id, farmer_id, quantity, unit_price, total_price, status)
    VALUES (p_buyer_id, p_crop_id, v_farmer_id, p_quantity, v_price, v_total_price, 'Pending');
    
    -- Update crop quantity
    UPDATE Crops SET quantity = quantity - p_quantity WHERE id = p_crop_id;
    
    -- Commit transaction
    COMMIT;
    
    SELECT 'Order placed successfully' as message, LAST_INSERT_ID() as order_id;
END//
DELIMITER ;

-- 8️⃣ Verify tables and data
SHOW TABLES;

-- Basic data verification
SELECT 'Users' as Table_Name, COUNT(*) as Count FROM Users
UNION ALL
SELECT 'Crops', COUNT(*) FROM Crops
UNION ALL
SELECT 'Orders', COUNT(*) FROM Orders
UNION ALL
SELECT 'Reviews', COUNT(*) FROM Reviews
UNION ALL
SELECT 'Wishlist', COUNT(*) FROM Wishlist
UNION ALL
SELECT 'Notifications', COUNT(*) FROM Notifications;

-- Sample queries for verification
SELECT * FROM Users LIMIT 3;
SELECT * FROM Crop_Details LIMIT 3;
SELECT * FROM Order_Details LIMIT 3;