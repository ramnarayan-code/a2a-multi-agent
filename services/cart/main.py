import os
import uvicorn
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events import EventQueue
from a2a.utils.message import new_agent_text_message
from services.shared.products import get_product_by_id
from services.shared.state_manager import state_manager

class CartExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message =  context.get_user_input()
        message_text = message if message else ""
        message_lower = message_text.lower()
        
        # Use simple session ID strategy for now, or extract from context if available
        session_id = "default" 
        
        resp = "I can help you add items to your cart or view cart contents."
        
        if "add" in message_lower:
            words = message_text.split()
            pid = next((w.upper() for w in words if any(prefix in w.upper() for prefix in ["ELEC", "HOME", "SPORT"])), None)
            if pid:
                product = get_product_by_id(pid)
                if not product: 
                    resp = "Product not found."
                else:
                    stock = state_manager.get_stock(pid)
                    if stock < 1: 
                        resp = "Insufficient stock."
                    else:
                        cart = state_manager.get_cart(session_id)
                        found = False
                        for item in cart["items"]:
                            if item["product_id"] == pid:
                                item["quantity"] += 1
                                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                                found = True
                                break
                        if not found:
                            cart["items"].append({
                                "product_id": pid, "name": product["name"], 
                                "price": product["price"], "quantity": 1, "subtotal": product["price"]
                            })
                        cart["total"] = round(sum(i["subtotal"] for i in cart["items"]), 2)
                        cart["item_count"] = sum(i["quantity"] for i in cart["items"])
                        state_manager.update_cart(session_id, cart)
                        resp = f"Added {product['name']} to cart. Total: ${cart['total']}"
            else:
                resp = "Please provide a valid product ID to add to cart."
            
        elif "view" in message_lower or "cart" in message_lower:
            cart = state_manager.get_cart(session_id)
            if not cart["items"]: 
                resp = "Your cart is empty."
            else:
                resp = "Your cart:\n"
                for i in cart["items"]:
                    resp += f"- {i['name']} x{i['quantity']} (${i['subtotal']})\n"
                resp += f"\nTotal: ${cart['total']}"
            
        await event_queue.enqueue_event(
            new_agent_text_message(text=resp, task_id=context.task_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass

skill = AgentSkill(
    id="cart_management",
    name="Cart Management",
    description="Manage shopping cart items",
    tags=["ecommerce", "cart", "shopping"],
    examples=["add this to my cart", "view my cart", "what is in my cart?"]
)
agent_card = AgentCard(
    name="CartAgent",
    description="Specialized agent for cart management",
    url=f"http://{os.getenv('SERVICE_NAME', 'cart-agent')}:8000",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill]
)

# Start A2A Server
# Start A2A Server
request_handler = DefaultRequestHandler(
    agent_executor=CartExecutor(),
    task_store=InMemoryTaskStore()
)
a2a_app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)
app = a2a_app.build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
