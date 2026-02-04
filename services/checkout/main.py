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
from services.shared.state_manager import state_manager

class CheckoutExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        session_id = "default"
        cart = state_manager.get_cart(session_id)
        
        if not cart["items"]:
            resp = "Your cart is empty. Nothing to checkout."
        else:
            out_of_stock = False
            for item in cart["items"]:
                if not state_manager.update_stock(item["product_id"], item["quantity"]):
                    resp = f"Sorry, {item['name']} is no longer in stock."
                    out_of_stock = True
                    break
            
            if not out_of_stock:
                order_id = state_manager.create_order({
                    "items": cart["items"],
                    "total": cart["total"],
                    "payment_method": "credit_card",
                    "status": "pending"
                })
                
                state_manager.clear_cart(session_id)
                resp = f"Checkout successful! Order ID: **{order_id}**. Total: ${cart['total']}."

        await event_queue.enqueue_event(
            new_agent_text_message(text=resp, task_id=context.task_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
# ...
# The middle part (skills/card) is skipped by replace_file_content if I just target top and bottom.
# I will use multi_replace for checkout and order to save calls if I can, but replace_file_content is safer for big blocks. I'll split into top/bottom updates for these too.

skill = AgentSkill(
    id="checkout",
    name="Checkout",
    description="Process order checkout",
    tags=["ecommerce", "checkout", "payment"],
    examples=["checkout my cart", "place order", "buy these items"]
)
agent_card = AgentCard(
    name="CheckoutAgent",
    description="Specialized agent for checkout",
    url=f"http://{os.getenv('SERVICE_NAME', 'checkout-agent')}:8000",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill]
)

# Start A2A Server
# Start A2A Server
request_handler = DefaultRequestHandler(
    agent_executor=CheckoutExecutor(),
    task_store=InMemoryTaskStore()
)
a2a_app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)
app = a2a_app.build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
