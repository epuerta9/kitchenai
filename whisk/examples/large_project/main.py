from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.services import StorageService, EmbeddingService, QueryService
from whisk.client import WhiskClient
from whisk.kitchenai_sdk.schema import DependencyType
from apps.chat import chat_app
from apps.rag import rag_app
from apps.tools import tools_app

# Create main app
main_app = KitchenAIApp(namespace="main")

# Initialize client
client = WhiskClient(
    nats_url="nats://localhost:4222",
    kitchen=main_app
)

# Create services and register as dependencies
storage_service = StorageService(client)
embedding_service = EmbeddingService(client)
query_service = QueryService(client)

main_app.register_dependency(DependencyType.STORAGE_SERVICE, storage_service)
main_app.register_dependency(DependencyType.EMBEDDING_SERVICE, embedding_service)
main_app.register_dependency(DependencyType.QUERY_SERVICE, query_service)

# Mount sub-apps (they'll inherit the service dependencies)
main_app.mount_app("chat", chat_app)
main_app.mount_app("rag", rag_app)
main_app.mount_app("tools", tools_app)

# The resulting handler paths would be:
# - /chat/basic
# - /chat/stream
# - /rag/search
# - /rag/ingest
# - /tools/calculator 