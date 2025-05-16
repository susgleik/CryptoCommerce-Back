# app/models/__init__.py
from .user_model import User, UserProfile
from .payment_model import PaymentMethod, UserPaymentMethod
from .product_model import Supplier, Product, Category, ProductCategory, ProductReview, ProductAttributeType, ProductAttributeValue
from .cart_model import ShoppingCart, CartItem, Wishlist, WishlistItem
from .order_model import Order, OrderItem
from .store_model import Store, StoreInventory, StoreStaff, PhysicalSale, PhysicalSaleItem
from .stats_model import SalesStatistics, InventoryMovement, AdminActionLog
from .discount_model import Discount, ProductDiscount, CategoryDiscount

# Para que SQLAlchemy cree todas las tablas en Base.metadata.create_all()
__all__ = [
    'User', 'UserProfile', 
    'PaymentMethod', 'UserPaymentMethod',
    'Supplier', 'Product', 'Category', 'ProductCategory', 'ProductReview', 'ProductAttributeType', 'ProductAttributeValue',
    'ShoppingCart', 'CartItem', 'Wishlist', 'WishlistItem',
    'Order', 'OrderItem',
    'Store', 'StoreInventory', 'StoreStaff', 'PhysicalSale', 'PhysicalSaleItem',
    'SalesStatistics', 'InventoryMovement', 'AdminActionLog',
    'Discount', 'ProductDiscount', 'CategoryDiscount'
]