from dataclasses import dataclass
from whisk.kitchenai_sdk.nats_schema import (
    NatsRegisterMessage,
    StorageGetRequestMessage,
    StorageGetResponseMessage,
    StorageResponseMessage,
    EmbedResponseMessage,
)
import json
import logging
import logging
from kitchenai.core.auth.oss.organization import OSSBentoClient
from whisk.client import WhiskClient
from django.conf import settings
from django.apps import apps
from datetime import datetime
from kitchenai.core.models.file import FileObject
from kitchenai.core.models.embed import EmbedObject
from kitchenai.core.models.file import StorageRequestMessage as StorageRequestMessageModel

logger = logging.getLogger(__name__)

@dataclass
class AccountLimits:
    mem_storage: str = "500M"
    disk_storage: str = "5G"
    streams: int = 10
    consumers: int = 100


whisk = WhiskClient(
    settings.WHISK_SETTINGS["nats_url"],
    user=settings.WHISK_SETTINGS["user"],
    password=settings.WHISK_SETTINGS["password"],
    is_kitchenai=True,
)
"""
"kitchenai.service.*.storage.*.response",
"kitchenai.service.*.storage.*.response.playground",
"kitchenai.service.*.query.*.stream.response",
"kitchenai.service.*.embedding.*.response",
"kitchenai.service.*.mgmt.register",

"""


@whisk.broker.subscriber("kitchenai.service.*.storage.*.response", "kitchenai-storage")
async def on_message(msg: StorageResponseMessage):
    """Updates the FileObject status and creates a StorageRequestMessage"""
    if msg.error:
        logger.error(f"Error in storage response: {msg.error}")
        return
    file_object = await FileObject.objects.aget(id=msg.id)
    await StorageRequestMessageModel.objects.acreate(
        file_object=file_object,
        request_id=msg.request_id,
        timestamp=msg.timestamp,
        label=msg.label,
        client_id=msg.client_id,
        metadata=msg.metadata,
        status=msg.status,
        token_counts=msg.token_counts,
    )
    file_object.status = FileObject.Status.COMPLETED
    await file_object.asave()


@whisk.broker.subscriber("kitchenai.service.*.storage.*.get", "kitchenai-storage-get")
async def on_message(msg: StorageGetRequestMessage):
    """Subscribe to storage get requests. Returns back a presigned url for the file"""
    file_object = await FileObject.objects.aget(id=msg.id)
    try:
        presigned_url = file_object.generate_presigned_url()
        return StorageGetResponseMessage(
            timestamp=msg.timestamp,
            request_id=msg.request_id,
            presigned_url=presigned_url,
            client_id=msg.client_id,
            label=msg.label,
        )
    except Exception as e:
        return StorageGetResponseMessage(
            timestamp=msg.timestamp,
            request_id=msg.request_id,
            error=str(e),
            client_id=msg.client_id,
            label=msg.label,
        )


@whisk.broker.subscriber(
    "kitchenai.service.*.query.*.stream.response", "kitchenai-query"
)
async def on_message(msg: str):
    print(msg)


@whisk.broker.subscriber(
    "kitchenai.service.*.embedding.*.response", "kitchenai-embedding"
)
async def on_message(msg: EmbedResponseMessage):
    if msg.error:
        logger.error(f"Error in embed response: {msg.error}")
        return
    
    #get the embedding object and update the status
    embedding = await EmbedObject.objects.aget(id=msg.id)
    embedding.status = EmbedObject.Status.COMPLETED
    await embedding.asave()
    print(msg)




@whisk.broker.subscriber("kitchenai.service.*.mgmt.register", "kitchenai-register")
async def on_message(msg: NatsRegisterMessage):
    """
    Handle Whisk client registration with NATS server
    FLOW:
    - Get an incoming unknown client ID (client ID is the name of the project in cloud but tied to org in OSS)
    - Check if we are in OSS mode then add the client ID
    - Send an acknowledgment back to the client
    """
    Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
    logger.info(f"Received registration message")
    if settings.KITCHENAI_LICENSE == "oss":
        # client ID is tied to default org
        try:

            # Get organization
            org = await Organization.objects.aget(name=Organization.DEFAULT_NAME)

            # check to see if OSSBentoClient exists
            try:
                oss_bento_client = await OSSBentoClient.objects.aget(
                    client_id=msg.client_id, version=msg.version, name=msg.name
                )
                # Client already exists
                # update the bento box

                oss_bento_client.last_seen = datetime.now()
                await oss_bento_client.asave()

                # send acknowledgment

                return NatsRegisterMessage(
                    client_id=msg.client_id,
                    ack=True,
                    message="client_id already registered",
                    bento_box=msg.bento_box.model_dump(),
                    version=msg.version,
                    client_type=msg.client_type,
                    client_description=msg.client_description,
                    name=msg.name,
                )
            except OSSBentoClient.DoesNotExist:
                # create a new OSSBentoClient
                oss_bento_client = await OSSBentoClient.objects.acreate(
                    client_id=msg.client_id,
                    organization=org,
                    client_description=msg.client_description,
                    message="Registration successful",
                    ack=True,
                    bento_box=msg.bento_box.model_dump(),
                    version=msg.version,
                    client_type=msg.client_type,
                    name=msg.name,
                    last_seen=datetime.now(),
                )

                # Send acknowledgment
                response = NatsRegisterMessage(
                    client_id=oss_bento_client.client_id,
                    ack=True,
                    message="Registration successful",
                    bento_box=oss_bento_client.bento_box,
                    version=oss_bento_client.version,
                    name=oss_bento_client.name,
                    client_type=oss_bento_client.client_type,
                    client_description=oss_bento_client.client_description,
                )

                logger.info(f"Client registered: {msg.client_id}")
                return response

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            response = NatsRegisterMessage(
                client_id=msg.client_id,
                ack=False,
                error=str(e),
                message=f"Registration failed: {str(e)}",
                bento_box=msg.bento_box.model_dump(),
                version=msg.version,
                name=msg.name,
                client_type=msg.client_type,
                client_description=msg.client_description,
            )
            return response
