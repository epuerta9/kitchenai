from django.conf import settings


async def register_client(client_id: str, client_type: str, client_description: str | None = None):
    if settings.KITCHENAI_LICENSE == "oss":
        pass
    else:
        pass

