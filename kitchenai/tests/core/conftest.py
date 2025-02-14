import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def sample_file():
    """Create a sample file for testing"""
    file_content = b"test content"
    return SimpleUploadedFile("test_file.txt", file_content) 