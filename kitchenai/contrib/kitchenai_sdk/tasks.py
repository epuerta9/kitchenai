from kitchenai.core.models import FileObject
import logging
import tempfile
from typing import Callable
from kitchenai.core.models import FileObject
from django.core.files.storage import default_storage
from django.core.mail import send_mail
import os

logger = logging.getLogger(__name__)

def process_file_task(storage_function: Callable, instance: FileObject, *args, **kwargs):
    """
    This is a task that will be run by the django task queue
    """

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
                result = storage_function(temp_dir, *args, extension=extension, **kwargs)

                # if results["is_llama_api"]:
                #     #update the is_llama_api object so we know for billing purposes we can see how many api calls
                #     #TODO: lifecycle hook to this field so its cleaner.
                #     project = Project.objects.get(pk=metadata["project_id"],projectuser__role="owner")
                #     project.is_llama_api = results["is_llama_api"]
                #     project.save()
                    

        return result
    except Exception as e:
        instance.status = FileObject.Status.FAILED
        instance.save()
        raise e
    finally:
        instance.status = FileObject.Status.COMPLETED
        instance.save()