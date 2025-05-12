-- data.sql - Script para crear estructura completa de base de datos de ecommerce genérico
-- Ejecutar directamente en DBeaver o cualquier cliente MySQL

-- Crear base de datos
DROP DATABASE IF EXISTS ecommerce;
CREATE DATABASE ecommerce;
USE ecommerce;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PAYMENT_METHODS
CREATE TABLE IF NOT EXISTS PAYMENT_METHODS (
    payment_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla SUPPLIERS (antes AUTHORS)
CREATE TABLE IF NOT EXISTS SUPPLIERS (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    supplier_image VARCHAR(255),
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCTS (antes BOOKS)
CREATE TABLE IF NOT EXISTS PRODUCTS (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    product_image VARCHAR(255),
    description TEXT,
    online_stock INT NOT NULL DEFAULT 0,
    sku VARCHAR(50) UNIQUE NOT NULL,
    release_date DATE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    product_type VARCHAR(100) DEFAULT 'general', -- Para diferenciar tipos de productos
    attributes JSON, -- Para almacenar atributos específicos según el tipo (ISBN para libros, peso para frutas, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla CATEGORIES
CREATE TABLE IF NOT EXISTS CATEGORIES (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_image VARCHAR(255),
    parent_category_id INT, -- Añadido para categorías jerárquicas
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCT_CATEGORIES
CREATE TABLE IF NOT EXISTS PRODUCT_CATEGORIES (
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla STORE_INVENTORY
CREATE TABLE IF NOT EXISTS STORE_INVENTORY (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    location VARCHAR(50),
    low_stock_threshold INT DEFAULT 5,
    notify_low_stock BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES STORES(store_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id),
    UNIQUE KEY (store_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla SHOPPING_CARTS
CREATE TABLE IF NOT EXISTS SHOPPING_CARTS (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla CART_ITEMS
CREATE TABLE IF NOT EXISTS CART_ITEMS (
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id, product_id),
    FOREIGN KEY (cart_id) REFERENCES SHOPPING_CARTS(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla ORDER_ITEMS
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PHYSICAL_SALE_ITEMS
CREATE TABLE IF NOT EXISTS PHYSICAL_SALE_ITEMS (
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    PRIMARY KEY (sale_id, product_id),
    FOREIGN KEY (sale_id) REFERENCES PHYSICAL_SALES(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla INVENTORY_MOVEMENTS
CREATE TABLE IF NOT EXISTS INVENTORY_MOVEMENTS (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    user_id INT NOT NULL,
    movement_type ENUM('entrada', 'salida', 'transferencia', 'ajuste', 'online_reserva') NOT NULL,
    quantity INT NOT NULL,
    reference VARCHAR(100),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id),
    FOREIGN KEY (store_id) REFERENCES STORES(store_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla SALES_STATISTICS
CREATE TABLE IF NOT EXISTS SALES_STATISTICS (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    total_online_sales INT DEFAULT 0,
    total_physical_sales INT DEFAULT 0,
    online_revenue DECIMAL(12, 2) DEFAULT 0.00,
    physical_revenue DECIMAL(12, 2) DEFAULT 0.00,
    views_count INT DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCT_REVIEWS
CREATE TABLE IF NOT EXISTS PRODUCT_REVIEWS (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating DECIMAL(3, 1) NOT NULL,
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCT_ATTRIBUTE_TYPES
CREATE TABLE IF NOT EXISTS PRODUCT_ATTRIBUTE_TYPES (
    attribute_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    product_type VARCHAR(100) NOT NULL,
    data_type ENUM('text', 'number', 'date', 'boolean') NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    is_searchable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCT_ATTRIBUTE_VALUES
CREATE TABLE IF NOT EXISTS PRODUCT_ATTRIBUTE_VALUES (
    value_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    attribute_type_id INT NOT NULL,
    text_value TEXT,
    number_value DECIMAL(10, 2),
    date_value DATE,
    boolean_value BOOLEAN,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_type_id) REFERENCES PRODUCT_ATTRIBUTE_TYPES(attribute_type_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla ADMIN_ACTIONS_LOG
CREATE TABLE IF NOT EXISTS ADMIN_ACTIONS_LOG (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla DISCOUNTS
CREATE TABLE IF NOT EXISTS DISCOUNTS (
    discount_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    discount_type ENUM('percentage', 'fixed_amount') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL, -- Porcentaje o monto fijo
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    min_purchase DECIMAL(10, 2) DEFAULT 0.00,
    max_uses INT,
    current_uses INT DEFAULT 0,
    coupon_code VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla PRODUCT_DISCOUNTS para aplicar descuentos a productos específicos
CREATE TABLE IF NOT EXISTS PRODUCT_DISCOUNTS (
    product_id INT NOT NULL,
    discount_id INT NOT NULL,
    PRIMARY KEY (product_id, discount_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (discount_id) REFERENCES DISCOUNTS(discount_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla CATEGORY_DISCOUNTS para aplicar descuentos a categorías completas
CREATE TABLE IF NOT EXISTS CATEGORY_DISCOUNTS (
    category_id INT NOT NULL,
    discount_id INT NOT NULL,
    PRIMARY KEY (category_id, discount_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE CASCADE,
    FOREIGN KEY (discount_id) REFERENCES DISCOUNTS(discount_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla WISHLISTS
CREATE TABLE IF NOT EXISTS WISHLISTS (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla WISHLIST_ITEMS
CREATE TABLE IF NOT EXISTS WISHLIST_ITEMS (
    wishlist_id INT NOT NULL,
    product_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    PRIMARY KEY (wishlist_id, product_id),
    FOREIGN KEY (wishlist_id) REFERENCES WISHLISTS(wishlist_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reactivar las restricciones de clave foránea
SET FOREIGN_KEY_CHECKS = 1;

-- Insertar algunos datos iniciales básicos para comenzar (opcional)

-- Insertar métodos de pago básicos
INSERT INTO PAYMENT_METHODS (name, description) VALUES 
('Tarjeta de crédito', 'Pago con tarjeta de crédito'),
('Tarjeta de débito', 'Pago con tarjeta de débito'),
('PayPal', 'Pago a través de PayPal'),
('Transferencia bancaria', 'Pago mediante transferencia bancaria'),
('Efectivo', 'Pago en efectivo (solo para recogida en tienda)');

-- Insertar categorías raíz básicas
INSERT INTO CATEGORIES (name, description, parent_category_id) VALUES 
('Productos destacados', 'Productos en promoción o destacados', NULL),
('Novedades', 'Productos recién llegados', NULL),
('Ofertas', 'Productos con descuento', NULL);

-- Crear usuario administrador por defecto (contraseña: admin123)
INSERT INTO USERS (username, email, password_hash, user_type) VALUES 
('admin', 'admin@example.com', '$2y$10$uLMf8RkRUZx6QvmJUeiL2Okki4BOE9dJI/Cnr/VJdckaUAA6RS1BG', 'admin');

-- Crear una tienda inicial
INSERT INTO STORES (name, address, phone, email) VALUES 
('Tienda Principal', 'Calle Principal 123, Ciudad', '123-456-7890', 'tienda@example.com');