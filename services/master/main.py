import os
import uuid
import httpx
import logging
import gradio as gr
from typing import Dict, Optional
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import SendMessageRequest, MessageSendParams

from services.shared.state_manager import state_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service Base URLs
BASE_URLS = {
    "search": f"http://{os.getenv('SERVICE_NAME_SEARCH', 'search-agent')}:8000",
    "cart": f"http://{os.getenv('SERVICE_NAME_CART', 'cart-agent')}:8000",
    "checkout": f"http://{os.getenv('SERVICE_NAME_CHECKOUT', 'checkout-agent')}:8000",
    "order": f"http://{os.getenv('SERVICE_NAME_ORDER', 'order-agent')}:8000"
}

# Cache for initialized clients
clients: Dict[str, A2AClient] = {}
http_client = httpx.AsyncClient()

async def get_client(service_key: str) -> Optional[A2AClient]:
    if service_key in clients:
        return clients[service_key]
    
    base_url = BASE_URLS.get(service_key)
    if not base_url:
        return None

    try:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=base_url)
        card = await resolver.get_agent_card()
        
        client = A2AClient(httpx_client=http_client, agent_card=card)
        clients[service_key] = client
        logger.info(f"Initialized client for {service_key}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize client for {service_key}: {e}")
        return None

async def route_request(message, history, session_id):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    msg_l = message.lower()
    service_key = None
    
    # Routing logic
    if any(k in msg_l for k in ["search", "find", "show", "look"]):
        service_key = "search"
    elif any(k in msg_l for k in ["add", "cart", "view"]):
        service_key = "cart"
    elif any(k in msg_l for k in ["checkout", "buy", "pay"]):
        service_key = "checkout"
    elif any(k in msg_l for k in ["status", "order", "track"]):
        service_key = "order"
    else:
        # Default fallback or error
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "I can help you search for products, manage your cart, checkout, or track orders."})
        return history, session_id, state_manager.get_cart(session_id)

    client = await get_client(service_key)
    if not client:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"Error: Could not connect to {service_key} agent."})
        return history, session_id, state_manager.get_cart(session_id)

    try:
        # Construct proper A2A message
        payload = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "message_id": uuid.uuid4().hex,
            }
        }
        
        request = SendMessageRequest(
            id=str(uuid.uuid4()), 
            params=MessageSendParams(**payload)
        )
        
        response_obj = await client.send_message(request)
        
        # Let's try to get text from the first part
        bot_text = "Received response"
        if response_obj and response_obj.root and response_obj.root.result:
             parts = response_obj.root.result.parts
             if parts and len(parts) > 0:
                 bot_text = parts[0].root.text

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_text})

    except Exception as e:
        logger.error(f"Error communicating with {service_key}: {e}")
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
    
    cart = state_manager.get_cart(session_id)
    return history, session_id, cart

def create_ui():
    with gr.Blocks(title="Distributed eCommerce Agents") as demo:
        session_id = gr.State()
        
        gr.Markdown("# 🛒 Distributed Multi-Agent eCommerce")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500)
                msg = gr.Textbox(placeholder="Ask anything...", label="Message")
                submit = gr.Button("Send", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🛍️ Cart Summary")
                cart_info = gr.JSON(value={"items": [], "total": 0.0})
                
        submit.click(route_request, [msg, chatbot, session_id], [chatbot, session_id, cart_info])
        msg.submit(route_request, [msg, chatbot, session_id], [chatbot, session_id, cart_info])
        
    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860)
