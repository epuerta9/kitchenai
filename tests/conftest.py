import logging
import os

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings

pytest_plugins = []  # type: ignore


def pytest_configure(config):
    logging.disable(logging.CRITICAL)


TEST_SETTINGS = {
    "DEBUG": False,
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    },
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "LOGGING_CONFIG": None,
    "PASSWORD_HASHERS": [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ],
    "Q_CLUSTER": {
        "sync": True,
    },
    "STORAGES": {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    "WHITENOISE_AUTOREFRESH": True,
}


@pytest.fixture(autouse=True, scope="session")
def use_test_settings():
    with override_settings(**TEST_SETTINGS):
        yield


@pytest.fixture(autouse=True)
def setup_test_environment():
    # Setup test environment variables
    os.environ["OPENAI_API_KEY"] = "test-key"

    # Configure Django settings
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'kitchenai.core',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.common.CommonMiddleware',
        ],
        ROOT_URLCONF='tests.urls',
        SECRET_KEY='test-key',
    )


@pytest.fixture
def test_file_content():
    return "This is a test document for vector storage"


@pytest.fixture
def uploaded_file(test_file_content):
    return SimpleUploadedFile(
        "test.txt",
        test_file_content.encode(),
        content_type="text/plain"
    )
