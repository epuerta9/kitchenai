import logging
import os
import tempfile
from collections.abc import Callable

from django.core.files.storage import default_storage
from kitchenai.core.models import (
    FileObject,
    EmbedObject,
    StorageFunctionTokenCounts,
    EmbedFunctionTokenCounts,
)
from kitchenai.core.utils import get_core_kitchenai_app
from .schema import EmbedSchema, StorageSchema, TokenCountSchema

logger = logging.getLogger(__name__)


def process_file_task_core(instance, *args, **kwargs):
    """process file async function for core app using storage task"""
    logger.info(f"processing file with id: {instance.ingest_label}")
    try:
        kitchenai_app = get_core_kitchenai_app()

        f = kitchenai_app.storage.get_task(instance.ingest_label)
        if f:
            return _process_file_task(f, instance)
        else:
            logger.warning(f"No storage task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in process_file_task_core: {e}")
        raise e


def _process_file_task(
    storage_function: Callable, instance: FileObject, *args, **kwargs
):
    """process file task"""
    instance.status = FileObject.Status.PROCESSING
    instance.save()
    file = instance.file
    temp_dir = tempfile.mkdtemp()
    _, extension = os.path.splitext(file.name)

    try:
        with default_storage.open(file.name) as f:
            with tempfile.NamedTemporaryFile(
                dir=temp_dir, suffix=f"_tmp{extension}"
            ) as temp_file:

                temp_file.write(f.read())
                # Calculate the size in MB
                file_size_bytes = temp_file.tell()
                file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to MB

                # Log the size for debugging
                logger.info(f"Size of the temporary file: {file_size_mb} MB")

                # Check if file size exceeds 20 MB
                if file_size_mb > 150:
                    logger.error(
                        f"File size {file_size_mb} MB exceeds the 150 MB limit."
                    )
                    raise Exception("File size exceeds 150 MB limit")

                if file_size_mb > 30:
                    logger.warning(
                        f"File size {file_size_mb} MB exceeds the 30 MB limit."
                    )
                    # TODO: add hook to notify other parts of the system

                temp_file.seek(0)
                metadata = {
                    "id": str(instance.pk),
                    "file_path": file.name,
                    "file_name": instance.name,
                    "source": "kitchenai",
                    "instance_label": instance.ingest_label,
                }
                logger.info(f"instance metadata: {instance.metadata}")

                if instance.metadata:
                    metadata.update(instance.metadata)

                logger.info(f"metadata: {metadata}")
                data = StorageSchema(
                    dir=temp_dir, metadata=metadata, extension=extension
                )
                result = storage_function(data, **kwargs)
                if result:
                    if result.token_counts:
                        t = (
                            result.token_counts
                            if isinstance(result.token_counts, TokenCountSchema)
                            else TokenCountSchema(**result.token_counts)
                        )
                        StorageFunctionTokenCounts.objects.create(
                            file_object=instance,
                            embedding_tokens=t.embedding_tokens,
                            llm_prompt_tokens=t.llm_prompt_tokens,
                            llm_completion_tokens=t.llm_completion_tokens,
                            total_llm_tokens=t.total_llm_tokens,
                        )

        value = {"storage_result": result, "ingest_label": instance.ingest_label}
        if result.token_counts:
            value["token_counts"] = t
        return value
    except Exception as e:
        instance.status = FileObject.Status.FAILED
        instance.save()
        raise e
    finally:
        instance.status = FileObject.Status.COMPLETED
        instance.save()


def delete_file_task_core(instance: FileObject, *args, **kwargs):
    """delete file async function for core app using storage task"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app.storage.get_hook(instance.ingest_label, "on_delete")
        if f:
            return f(instance, *args, **kwargs)
        else:
            logger.warning(f"No delete task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in delete_file_task_core: {e}")
        raise e


def _embed_task(embed_function: Callable, instance: EmbedObject, *args, **kwargs):
    """embed task"""
    instance.status = EmbedObject.Status.PROCESSING
    instance.save()
    metadata = {
        "id": str(instance.pk),
        "text": instance.text,
        "source": "kitchenai",
        "instance_label": instance.ingest_label,
    }

    metadata.update(instance.metadata)

    try:
        result = embed_function(
            EmbedSchema(text=instance.text, metadata=metadata), **kwargs
        )
        if result.token_counts:
            t = (
                result.token_counts
                if isinstance(result.token_counts, TokenCountSchema)
                else TokenCountSchema(**result.token_counts)
            )

            EmbedFunctionTokenCounts.objects.create(
                embed_object=instance,
                embedding_tokens=t.embedding_tokens,
                llm_prompt_tokens=t.llm_prompt_tokens,
                llm_completion_tokens=t.llm_completion_tokens,
                total_llm_tokens=t.total_llm_tokens,
            )
        value = {"embed_result": result, "ingest_label": instance.ingest_label}
        if result.token_counts:
            value["token_counts"] = t
        return value
    except Exception as e:
        instance.status = EmbedObject.Status.FAILED
        instance.save()
        raise e
    finally:
        instance.status = EmbedObject.Status.COMPLETED
        instance.save()


def embed_task_core(instance: EmbedObject, *args, **kwargs):
    """process file async function for core app using storage task"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app.embeddings.get_task(instance.ingest_label)
        if f:
            return _embed_task(f, instance, **kwargs)
        else:
            logger.warning(f"No embed task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in embed_task_core: {e}")
        raise e


def delete_embed_task_core(instance: EmbedObject, *args, **kwargs):
    """delete embed task for core app"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app.embeddings.get_hook(instance.ingest_label, "on_delete")
        if f:
            return f(instance, *args, **kwargs)
        else:
            logger.warning(f"No delete embed task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in delete_embed_task_core: {e}")
        raise e
