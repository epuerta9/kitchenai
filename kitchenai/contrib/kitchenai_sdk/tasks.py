import logging
import os
import tempfile
from collections.abc import Callable

from django.core.files.storage import default_storage
from kitchenai.core.models import FileObject, EmbedObject
from kitchenai.core.utils import get_core_kitchenai_app
import importlib

logger = logging.getLogger(__name__)

def process_file_task_app(storage_function: Callable, instance: FileObject, *args, **kwargs):
    """
    process file async function for django apps
    """
    return _process_file_task(storage_function, instance, *args, **kwargs)


def process_file_task_core(instance: FileObject, *args, **kwargs):
    """process file async function for core app using storage task"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app.storage_tasks(instance.ingest_label)
        if f:
            return _process_file_task(f, instance)
        else:
            logger.warning(f"No storage task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in run_task: {e}")

def _process_file_task(storage_function: Callable, instance: FileObject, *args, **kwargs):
    """process file task"""
    instance.status = FileObject.Status.PROCESSING
    instance.save()
    file = instance.file
    temp_dir = tempfile.mkdtemp()
    _, extension = os.path.splitext(file.name)

    try:
        with default_storage.open(file.name) as f:
            with tempfile.NamedTemporaryFile(dir=temp_dir, suffix=f"_tmp{extension}") as temp_file:

                temp_file.write(f.read())
                # Calculate the size in MB
                file_size_bytes = temp_file.tell()
                file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to MB

                # Log the size for debugging
                logger.info(f"Size of the temporary file: {file_size_mb} MB")

                # Check if file size exceeds 20 MB
                if file_size_mb > 150:
                    logger.error(f"File size {file_size_mb} MB exceeds the 150 MB limit.")
                    raise Exception("File size exceeds 150 MB limit")

                if file_size_mb > 30:
                    logger.warning(f"File size {file_size_mb} MB exceeds the 30 MB limit.")
                    #TODO: add hook to notify other parts of the system

                temp_file.seek(0)
                metadata = {"file_id": instance.pk, "file_name": file.name, "source": "kitchenai_cookbook", "file_label": instance.name}
                result = storage_function(temp_dir, *args, extension=extension, metadata=metadata, **kwargs)


        return {
            "storage_result": result,
            "ingest_label": instance.ingest_label
        }
    except Exception as e:
        instance.status = FileObject.Status.FAILED
        instance.save()
        raise e
    finally:
        instance.status = FileObject.Status.COMPLETED
        instance.save()

#DELETES

def delete_file_task_app(delete_function: Callable, instance: FileObject, *args, **kwargs):
    """
    delete file async function for django apps
    """
    return delete_function(instance, *args, **kwargs)


def delete_file_task_core(instance: FileObject, *args, **kwargs):
    """delete file async function for core app using storage task"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app.storage_delete_tasks(instance.ingest_label)
        if f:
            return f(instance, *args, **kwargs)
        else:
            logger.warning(f"No delete task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in run_task: {e}")

def _embed_task(embed_function: Callable, instance: EmbedObject, *args, **kwargs):
    """embed task"""
    instance.status = EmbedObject.Status.PROCESSING
    instance.save()
    metadata = {"object_id": instance.pk, "text": instance.text, "source": "kitchenai_cookbook", "object_label": instance.ingest_label}

    metadata.update(instance.metadata)
    
    try:
        result = embed_function(instance, metadata=metadata, **kwargs)

        return {
            "embed_result": result,
            "ingest_label": instance.ingest_label
        }
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
        f = kitchenai_app._embed_tasks.get(f"{kitchenai_app._namespace}.{instance.ingest_label}")
        if f:
            module_path, func_name = f.rsplit(".", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            return _embed_task(func, instance, **kwargs)
        else:
            logger.warning(f"No embed task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in run_task: {e}")

def delete_embed_task_core(instance: EmbedObject, *args, **kwargs):
    """delete embed task for core app"""
    try:
        kitchenai_app = get_core_kitchenai_app()
        f = kitchenai_app._embed_delete_tasks.get(f"{kitchenai_app._namespace}.{instance.ingest_label}")
        if f:
            module_path, func_name = f.rsplit(".", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            return func(instance, *args, **kwargs)
        else:
            logger.warning(f"No delete embed task found for {instance.ingest_label}")
    except Exception as e:
        logger.error(f"Error in run_task: {e}")

