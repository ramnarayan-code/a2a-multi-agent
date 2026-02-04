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
from services.shared.products import PRODUCTS

class SearchExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message =  context.get_user_input()
        query = message.lower() if message else ""
            
        # Simple keyword extraction
        stop_words = {"search", "find", "show", "me", "products", "look", "for", "a", "an", "the", "in", "with", "please"}
        query_parts = [w for w in query.split() if w not in stop_words]
        
        results = []
        if query_parts:
            for p in PRODUCTS:
                # Combine fields for checking
                product_text = (p["name"] + " " + p["description"] + " " + p["category"]).lower()
                
                # Check if any useful keyword is present in the product text
                if any(part in product_text for part in query_parts):
                    results.append(p)
        
        if not results:
            resp = "I couldn't find any products matching your search."
        else:
            resp = "I found these products for you:\n\n"
            for p in results:
                resp += f"- **{p['name']}** ({p['product_id']}): ${p['price']} - {p['description']}\n"
        
        await event_queue.enqueue_event(
            new_agent_text_message(text=resp, task_id=context.task_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass

# ... (AgentSkill and AgentCard definitions are preserved)
# But I need to preserve them, so I should be careful not to overwrite them if I can't see them.
# I'll just change the import and the bottom part.

# ...


# ... (AgentSkill and AgentCard definitions remain the same, so I will target around them or just replace the end of file)

# To allow maintaining the file structure without reading everything, I will replace the imports and the class definition part, and then the instantiation at the end. Use multi_replace if needed or just one big replace if context is contiguous.
# The file is small (60 lines). I can probably replace the whole file or large chunks.

# Let's try to replace imports and class first.


# A2A Configuration
skill = AgentSkill(
    id="product_search",
    name="Product Search",
    description="Search for products by name or description",
    tags=["ecommerce", "search", "products"],
    examples=["find a laptop", "search for running shoes"]
)

agent_card = AgentCard(
    name="SearchAgent",
    description="Specialized agent for product discovery",
    url=f"http://{os.getenv('SERVICE_NAME', 'search-agent')}:8000",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill]
)

# Start A2A Server
# Start A2A Server
request_handler = DefaultRequestHandler(
    agent_executor=SearchExecutor(),
    task_store=InMemoryTaskStore()
)
a2a_app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)
app = a2a_app.build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
