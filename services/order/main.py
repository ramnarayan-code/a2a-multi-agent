import os
import re
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

class OrderExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message =  context.get_user_input()
        message_text = message if message else ""
        
        match = re.search(r'ORD-\d+-\d+', message_text.upper())
        if match:
            order_id = match.group(0)
            order = state_manager.get_order(order_id)
            if order:
                resp = f"Order **{order_id}** is currently **{order['status']}**. Total: ${order['total']}."
            else:
                resp = "Order not found."
        else:
            resp = "Please provide an order ID (e.g. ORD-20260204-0001) to check status."

        await event_queue.enqueue_event(
            new_agent_text_message(text=resp, task_id=context.task_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass

skill = AgentSkill(
    id="order_status",
    name="Order Status",
    description="Track order status",
    tags=["ecommerce", "orders", "tracking"],
    examples=["where is my order?", "track order ORD-123"]
)
agent_card = AgentCard(
    name="OrderStatusAgent",
    description="Specialized agent for order tracking",
    url=f"http://{os.getenv('SERVICE_NAME', 'order-agent')}:8000",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill]
)

# Start A2A Server
# Start A2A Server
request_handler = DefaultRequestHandler(
    agent_executor=OrderExecutor(),
    task_store=InMemoryTaskStore()
)
a2a_app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)
app = a2a_app.build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
