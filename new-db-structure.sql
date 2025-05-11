-- Crear base de datos (opcional)
CREATE DATABASE IF NOT EXISTS bookstore;
USE bookstore;

-- Desactivar las restricciones de clave foránea temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- Tabla USERS
CREATE TABLE IF NOT EXISTS USERS (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('common', 'admin', 'store_staff') DEFAULT 'common',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Tabla USER_PROFILES
CREATE TABLE IF NOT EXISTS USER_PROFILES (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    address TEXT,
    phone VARCHAR(20),
    profile_image VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Tabla PAYMENT_METHODS
CREATE TABLE IF NOT EXISTS PAYMENT_METHODS (
    payment_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla USER_PAYMENT_METHODS
CREATE TABLE IF NOT EXISTS USER_PAYMENT_METHODS (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    payment_type_id INT NOT NULL,
    account_details VARCHAR(255) NOT NULL, -- debe encriptarse en la aplicación
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (payment_type_id) REFERENCES PAYMENT_METHODS(payment_type_id)
);

-- Tabla AUTHORS
CREATE TABLE IF NOT EXISTS AUTHORS (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    biography TEXT,
    author_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla BOOKS
CREATE TABLE IF NOT EXISTS BOOKS (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cover_image VARCHAR(255),
    description TEXT,
    online_stock INT NOT NULL DEFAULT 0,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    publication_date DATE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES AUTHORS(author_id)
);

-- Tabla CATEGORIES
CREATE TABLE IF NOT EXISTS CATEGORIES (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_image VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla BOOK_CATEGORIES (tabla de relación muchos a muchos)
CREATE TABLE IF NOT EXISTS BOOK_CATEGORIES (
    book_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE CASCADE
);

-- Tabla STORES
CREATE TABLE IF NOT EXISTS STORES (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(150),
    opening_hours TIME,
    closing_hours TIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla STORE_INVENTORY
CREATE TABLE IF NOT EXISTS STORE_INVENTORY (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    shelf_location VARCHAR(50),
    low_stock_threshold INT DEFAULT 5,
    notify_low_stock BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES STORES(store_id),
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id),
    UNIQUE KEY (store_id, book_id)
);

-- Tabla STORE_STAFF
CREATE TABLE IF NOT EXISTS STORE_STAFF (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    store_id INT NOT NULL,
    role ENUM('manager', 'cashier', 'inventory') NOT NULL,
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (store_id) REFERENCES STORES(store_id)
);

-- Tabla SHOPPING_CARTS
CREATE TABLE IF NOT EXISTS SHOPPING_CARTS (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Tabla CART_ITEMS
CREATE TABLE IF NOT EXISTS CART_ITEMS (
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id, book_id),
    FOREIGN KEY (cart_id) REFERENCES SHOPPING_CARTS(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id)
);

-- Tabla ORDERS
CREATE TABLE IF NOT EXISTS ORDERS (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    payment_type_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'processing', 'paid', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT NOT NULL,
    tracking_number VARCHAR(100),
    delivery_method ENUM('shipping', 'store_pickup') NOT NULL,
    store_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (payment_type_id) REFERENCES PAYMENT_METHODS(payment_type_id),
    FOREIGN KEY (store_id) REFERENCES STORES(store_id)
);

-- Tabla ORDER_ITEMS
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, book_id),
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id)
);

-- Tabla PHYSICAL_SALES
CREATE TABLE IF NOT EXISTS PHYSICAL_SALES (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('efectivo', 'tarjeta', 'otro') NOT NULL,
    receipt_number VARCHAR(50) NOT NULL,
    is_invoice_required BOOLEAN DEFAULT FALSE,
    customer_tax_info VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES STORES(store_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- Tabla PHYSICAL_SALE_ITEMS
CREATE TABLE IF NOT EXISTS PHYSICAL_SALE_ITEMS (
    sale_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    PRIMARY KEY (sale_id, book_id),
    FOREIGN KEY (sale_id) REFERENCES PHYSICAL_SALES(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id)
);

-- Tabla INVENTORY_MOVEMENTS
CREATE TABLE IF NOT EXISTS INVENTORY_MOVEMENTS (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    store_id INT NOT NULL,
    user_id INT NOT NULL,
    movement_type ENUM('entrada', 'salida', 'transferencia', 'ajuste', 'online_reserva') NOT NULL,
    quantity INT NOT NULL,
    reference VARCHAR(100),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id),
    FOREIGN KEY (store_id) REFERENCES STORES(store_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- Tabla SALES_STATISTICS
CREATE TABLE IF NOT EXISTS SALES_STATISTICS (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    total_online_sales INT DEFAULT 0,
    total_physical_sales INT DEFAULT 0,
    online_revenue DECIMAL(12, 2) DEFAULT 0.00,
    physical_revenue DECIMAL(12, 2) DEFAULT 0.00,
    views_count INT DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id) ON DELETE CASCADE
);

-- Tabla ADMIN_ACTIONS_LOG
CREATE TABLE IF NOT EXISTS ADMIN_ACTIONS_LOG (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- Reactivar las restricciones de clave foránea
SET FOREIGN_KEY_CHECKS = 1;