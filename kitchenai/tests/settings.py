from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'test-key-not-for-production'
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'kitchenai.core',
    'kitchenai.bento',  # Required due to model dependencies
]

MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

# Auth settings
AUTH_USER_MODEL = 'core.OSSUser'
AUTH_ORGANIZATION_MODEL = 'core.OSSOrganization'
AUTH_ORGANIZATIONMEMBER_MODEL = 'core.OSSOrganizationMember'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Required test settings
USE_TZ = False

# KitchenAI specific settings
KITCHENAI_LOCAL = True
KITCHENAI_SENTRY = False
KITCHENAI_LICENSE = 'oss'
KITCHENAI_BENTO_CLIENT_MODEL = 'core.OSSBentoClient'

# Media settings
MEDIA_ROOT = BASE_DIR / 'test_media'
MEDIA_URL = '/media/'

# Required for file uploads in tests
KITCHENAI_DB_DIR = BASE_DIR / 'test_kitchenai'
KITCHENAI_DB_DIR.mkdir(exist_ok=True)

# Whisk settings required by broker
WHISK_SETTINGS = {
    "user": "test_user",
    "password": "test_password",
    "nats_url": "nats://localhost:4222"
} 