from typing import List, Dict, Any

PRODUCTS = [
    {
        "product_id": "ELEC001",
        "name": "Wireless Bluetooth Headphones",
        "description": "Premium noise-cancelling over-ear headphones with 30-hour battery life",
        "price": 149.99,
        "stock": 25,
        "category": "Electronics"
    },
    {
        "product_id": "ELEC002",
        "name": "4K Smart TV 55\"",
        "description": "Ultra HD smart television with HDR and built-in streaming apps",
        "price": 599.99,
        "stock": 15,
        "category": "Electronics"
    },
    {
        "product_id": "ELEC003",
        "name": "Laptop Stand (Aluminum)",
        "description": "Ergonomic adjustable laptop stand for improved posture",
        "price": 49.99,
        "stock": 50,
        "category": "Electronics"
    },
    {
        "product_id": "HOME001",
        "name": "Coffee Maker (12-cup)",
        "description": "Programmable drip coffee maker with thermal carafe",
        "price": 79.99,
        "stock": 30,
        "category": "Home & Garden"
    },
    {
        "product_id": "HOME002",
        "name": "Memory Foam Pillow",
        "description": "Contoured memory foam pillow for neck and spine support",
        "price": 34.99,
        "stock": 100,
        "category": "Home & Garden"
    },
    {
        "product_id": "HOME003",
        "name": "LED Desk Lamp",
        "description": "Adjustable LED lamp with multiple brightness levels and USB charging port",
        "price": 39.99,
        "stock": 40,
        "category": "Home & Garden"
    },
    {
        "product_id": "SPORT001",
        "name": "Yoga Mat (6mm)",
        "description": "Non-slip exercise mat with carrying strap",
        "price": 24.99,
        "stock": 75,
        "category": "Sports & Outdoors"
    },
    {
        "product_id": "SPORT002",
        "name": "Water Bottle (32oz Insulated)",
        "description": "Stainless steel vacuum-insulated water bottle, keeps cold 24h",
        "price": 29.99,
        "stock": 60,
        "category": "Sports & Outdoors"
    },
    {
        "product_id": "SPORT003",
        "name": "Resistance Bands Set",
        "description": "Set of 5 resistance bands with different tension levels and door anchor",
        "price": 19.99,
        "stock": 85,
        "category": "Sports & Outdoors"
    },
    {
        "product_id": "SPORT004",
        "name": "Running Shoes (Men's)",
        "description": "Lightweight running shoes with responsive cushioning",
        "price": 89.99,
        "stock": 45,
        "category": "Sports & Outdoors"
    }
]

def get_product_by_id(product_id: str) -> Dict[str, Any]:
    return next((p for p in PRODUCTS if p["product_id"] == product_id), None)
