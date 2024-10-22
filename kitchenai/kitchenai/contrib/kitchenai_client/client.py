import json
import mimetypes
import os
from typing import Any

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

class KitchenClient:
    def __init__(self, config: dict[str, Any] | None = None, **kwargs):
        self._config = config or {}
        self.app_id = kwargs.get('app_id', "kitchenai")
        self._namespace = kwargs.get('namespace', "default")

    def __enter__(self):
        self._dapr_client = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._dapr_client:
            self._dapr_client.close()

    def dapr_id(self, target: str) -> 'KitchenClient':
        self.app_id = target
        return self

    def namespace(self, namespace: str) -> 'KitchenClient':
        self._namespace = namespace
        return self

    def _create_path(self, route_path: str, label: str) -> str:
        return f"/{self._namespace}/{route_path}/{label}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def query(self, query: str, label: str, **kwargs) -> str:
        path = self._create_path("query", label)
        data = {"query": query, **kwargs}
        return self.invoke(data, route=path)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def invoke(self, data: dict[str, Any], namespace: str | None = None, route: str | None = None) -> str:
        namespace = namespace or self._namespace
        if not route:
            raise ValueError("Route must be specified")

        if not self._dapr_client:
            raise RuntimeError("DaprClient is not initialized. Use 'with' statement or initialize manually.")

        try:
            resp = self._dapr_client.invoke_method(
                app_id=self.app_id,
                method_name=route,
                data=json.dumps(data),
                http_verb='POST',
                content_type='application/json'
            )
            return resp.text()
        except Exception as e:
            print(f"Error invoking method: {e}")
            raise

    def storage(self, label: str, **kwargs) -> str:
        path = self._create_path("storage", label)
        return self.invoke(kwargs, route=path)

    def embedding(self, label: str, **kwargs) -> str:
        path = self._create_path("embedding", label)
        return self.invoke(kwargs, route=path)

    def runnable(self, label: str, **kwargs) -> str:
        path = self._create_path("runnable", label)
        return self.invoke(kwargs, route=path)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload_file(self, file_path: str, label: str, **kwargs) -> str:
        if not self._dapr_client:
            raise RuntimeError("DaprClient is not initialized. Use 'with' statement or initialize manually.")

        # Read the file content
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Determine the content type based on the file type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'

        # Override content type for specific file extensions
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.md':
            content_type = 'text/markdown'
        elif file_extension == '.txt':
            content_type = 'text/plain'

        # Prepare metadata
        metadata = [
            ('filename', os.path.basename(file_path)),
            ('filesize', str(len(file_content))),
            ('content-type', content_type)
        ]

        # Create the path for file upload
        path = self._create_path("storage", label)

        try:
            resp = self._dapr_client.invoke_method(
                app_id=self.app_id,
                method_name=path,
                data=file_content,
                http_verb='POST',
                content_type=content_type,
                metadata=metadata
            )
            return resp.text()
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise

# Example usage:
# with KitchenClient(app_id="myapp", namespace="default") as client:
#     response = client.upload_file("/path/to/file.pdf", "upload-pdf")
#     print(response)
