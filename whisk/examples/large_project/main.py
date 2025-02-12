from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from apps.chat import chat_app
from apps.rag import rag_app
from apps.tools import tools_app
from dependencies import setup_dependencies

# Create main app
kitchen = KitchenAIApp(namespace="main")

# Setup shared dependencies
setup_dependencies(kitchen)

# Mount sub-apps with prefixes
kitchen.mount_app("/chat", chat_app)  # Will prefix handlers with /chat/
kitchen.mount_app("/rag", rag_app)    # Will prefix handlers with /rag/
kitchen.mount_app("/tools", tools_app) # Will prefix handlers with /tools/

# The resulting handler paths would be:
# - /chat/basic
# - /chat/stream
# - /rag/search
# - /rag/ingest
# - /tools/calculator 