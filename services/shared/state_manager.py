import json
import os
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime

class RedisStateManager:
    def __init__(self, host='redis', port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def get_cart(self, session_id: str) -> Dict[str, Any]:
        cart_json = self.r.get(f"cart:{session_id}")
        if cart_json:
            return json.loads(cart_json)
        return {"items": [], "total": 0.0, "item_count": 0}

    def update_cart(self, session_id: str, cart_data: Dict[str, Any]):
        self.r.set(f"cart:{session_id}", json.dumps(cart_data))

    def clear_cart(self, session_id: str):
        self.r.delete(f"cart:{session_id}")

    def create_order(self, order_data: Dict[str, Any]) -> str:
        order_count = self.r.incr("order_counter")
        date_str = datetime.now().strftime("%Y%m%d")
        order_id = f"ORD-{date_str}-{order_count:04d}"
        
        order_data["order_id"] = order_id
        order_data["created_at"] = datetime.now().isoformat()
        order_data["updated_at"] = datetime.now().isoformat()
        
        self.r.set(f"order:{order_id}", json.dumps(order_data))
        return order_id

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        order_json = self.r.get(f"order:{order_id}")
        if order_json:
            return json.loads(order_json)
        return None

    def update_stock(self, product_id: str, quantity: int) -> bool:
        # In this demo, stock is initially what's in products.py
        # We search redis for overrides first
        stock_key = f"stock:{product_id}"
        current_stock = self.r.get(stock_key)
        
        if current_stock is None:
            from services.shared.products import get_product_by_id
            product = get_product_by_id(product_id)
            if not product: return False
            current_stock = product["stock"]
            self.r.set(stock_key, current_stock)
        
        current_stock = int(current_stock)
        if current_stock >= quantity:
            self.r.decrby(stock_key, quantity)
            return True
        return False

    def get_stock(self, product_id: str) -> int:
        stock_key = f"stock:{product_id}"
        current_stock = self.r.get(stock_key)
        if current_stock is None:
            from services.shared.products import get_product_by_id
            product = get_product_by_id(product_id)
            return product["stock"] if product else 0
        return int(current_stock)

# Initialize global state manager
state_manager = RedisStateManager(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)
