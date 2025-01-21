import uuid

from django.db import models
from falco_toolbox.models import TimeStamped
from django.conf import settings
import boto3
from storages.backends.s3boto3 import S3Boto3Storage

def file_object_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/{uuid.uuid4()}/{filename}"


class FileObject(TimeStamped):
    """
    This is a model for any file that is uploaded to the system.
    It will be used to trigger any storage tasks or other processes
    """

    class Status(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    file = models.FileField(upload_to=file_object_directory_path)
    bento_box = models.ForeignKey(
        settings.KITCHENAI_BENTO_CLIENT_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    ingest_label = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default=Status.PENDING)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.name


    def generate_presigned_url(self, expires_in=3600):
        """
        Generate a pre-signed URL for the file.
        :param expires_in: Time in seconds for the URL to remain valid.
        :return: A pre-signed URL string.
        """
        if not self.file:
            return None

        storage = self.file.storage
        try:
            # Generate the pre-signed URL
            url = storage.connection.meta.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': storage.bucket_name,
                    'Key': self.file.name,
                },
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            # Log the error for debugging
            print(f"Error generating pre-signed URL: {e}")
            return None


class StorageFunctionTokenCounts(models.Model):
    file_object = models.ForeignKey(FileObject, on_delete=models.CASCADE)
    embedding_tokens = models.IntegerField(default=0)
    llm_prompt_tokens = models.IntegerField(default=0)
    llm_completion_tokens = models.IntegerField(default=0)
    total_llm_tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.file_object.name} - {self.total_llm_tokens} tokens"


class StorageRequestMessage(models.Model):
    file_object = models.ForeignKey(FileObject, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=255)
    timestamp = models.FloatField()
    label = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    metadata = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=50)
    token_counts = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.file_object.name} - {self.request_id}"

