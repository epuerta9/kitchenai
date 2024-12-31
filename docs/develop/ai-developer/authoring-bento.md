I'll show you a few examples of how to create custom Bento boxes using this framework.

### Example 1: Simple LLM Bento
This example creates a basic Bento that just manages an LLM:

```python:my_llm_bento/apps.py
from kitchenai_rag_simple_bento.base import BentoBaseConfig
from kitchenai_rag_simple_bento.types import DependencyType
from kitchenai.contrib.kitchenai_sdk.manager import DependencyManager

class SimpleLLMBentoConfig(BentoBaseConfig):
    name = "my_llm_bento"
    
    def __init__(self, app_name, app_module):
        dependency_manager = DependencyManager.get_instance(app_name)
        super().__init__(app_name, app_module, dependency_manager)
    
    def get_settings_key(self) -> str:
        return "MY_LLM_BENTO_SETTINGS"
    
    def create_dependencies(self, config: dict) -> dict[DependencyType, Any]:
        return {
            DependencyType.LLM: self._create_llm(config)
        }
        
    def _create_llm(self, config: dict):
        from langchain.llms import OpenAI
        return OpenAI(
            api_key=config['openai_api_key'],
            model_name=config.get('model_name', 'gpt-3.5-turbo')
        )
```

Settings would look like:
```python:settings.py
MY_LLM_BENTO_SETTINGS = {
    'openai_api_key': 'sk-...',
    'model_name': 'gpt-4'
}
```

### Example 2: Custom Document Store Bento
This example creates a Bento for document storage with custom dependency types:

```python:document_store_bento/types.py
from enum import Enum

class DocumentDependencyType(Enum):
    DOCUMENT_STORE = "document_store"
    FILE_PROCESSOR = "file_processor"
    METADATA_STORE = "metadata_store"
```

```python:document_store_bento/apps.py
from kitchenai_rag_simple_bento.base import BentoBaseConfig
from .types import DocumentDependencyType
from kitchenai.contrib.kitchenai_sdk.manager import DependencyManager

class DocumentStoreBentoConfig(BentoBaseConfig):
    name = "document_store_bento"
    
    def __init__(self, app_name, app_module):
        dependency_manager = DependencyManager.get_instance(app_name)
        super().__init__(app_name, app_module, dependency_manager)
    
    def get_settings_key(self) -> str:
        return "DOCUMENT_STORE_SETTINGS"
    
    def create_dependencies(self, config: dict) -> dict[DocumentDependencyType, Any]:
        return {
            DocumentDependencyType.DOCUMENT_STORE: self._create_document_store(config),
            DocumentDependencyType.FILE_PROCESSOR: self._create_file_processor(config),
            DocumentDependencyType.METADATA_STORE: self._create_metadata_store(config)
        }
    
    def _create_document_store(self, config: dict):
        if config['store_type'] == 's3':
            from my_storage import S3DocumentStore
            return S3DocumentStore(
                bucket=config['bucket_name'],
                prefix=config['prefix']
            )
        else:
            from my_storage import LocalDocumentStore
            return LocalDocumentStore(path=config['storage_path'])
            
    def _create_file_processor(self, config: dict):
        from my_processors import UniversalFileProcessor
        return UniversalFileProcessor(
            supported_types=config['supported_file_types']
        )
        
    def _create_metadata_store(self, config: dict):
        from my_metadata import SQLMetadataStore
        return SQLMetadataStore(
            connection_string=config['db_connection']
        )
```

### Example 3: Using the Bento in Your Code

```python:my_app/views.py
from document_store_bento.apps import DocumentStoreBentoConfig
from document_store_bento.types import DocumentDependencyType

class DocumentUploadView(APIView):
    def __init__(self):
        self.bento = apps.get_app_config('document_store_bento')
        
    def post(self, request):
        # Get dependencies
        doc_store = self.bento.get_dependency(DocumentDependencyType.DOCUMENT_STORE)
        processor = self.bento.get_dependency(DocumentDependencyType.FILE_PROCESSOR)
        
        # Use dependencies
        processed_doc = processor.process(request.FILES['document'])
        doc_id = doc_store.store(processed_doc)
        
        return Response({'document_id': doc_id})

    def update_config(self, new_config):
        # Dynamically update configuration
        self.bento.update_runtime_config(**new_config)
```

Key points about using the framework:

1. **Dependency Types**:
   - Define your own dependency types using Enums
   - Use these types consistently in your code

2. **Configuration**:
   - Settings are managed through Django settings
   - Can be updated at runtime using `update_runtime_config`

3. **Dependency Access**:
   - Use `get_dependency()` to access dependencies
   - Dependencies are lazy-loaded and cached

4. **Best Practices**:
   - Keep dependency creation methods private
   - Use type hints for better code clarity
   - Handle configuration errors gracefully
   - Document expected configuration format

5. **Testing**:
   - Easy to mock dependencies for testing
   - Can inject test configurations easily

This framework makes it easy to:
- Manage complex dependencies
- Switch implementations based on configuration
- Update dependencies at runtime
- Keep your code organized and testable
