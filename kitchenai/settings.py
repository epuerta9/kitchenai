import multiprocessing
import os
from email.utils import parseaddr
from pathlib import Path
import warnings
import logging

import djp
import sentry_sdk
from environs import Env
from falco_toolbox.sentry import sentry_profiles_sampler, sentry_traces_sampler
from marshmallow.validate import Email, OneOf
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# 0. Setup
# --------------------------------------------------------------------------------------------
from kitchenai import __version__ 

VERSION = __version__

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

APPS_DIR = BASE_DIR / "kitchenai"

KITCHENAI_DB_DIR = BASE_DIR / ".kitchenai"

KITCHENAI_DB_DIR.mkdir(exist_ok=True)

env = Env()
env.read_env(Path(BASE_DIR, ".env").as_posix())

# We should strive to only have two possible runtime scenarios: either `DEBUG`
# is True or it is False. `DEBUG` should be only true in development, and
# False when deployed, whether or not it's a production environment.
DEBUG = env.bool("DEBUG", default=False)
KITCHENAI_LOCAL = env.bool("KITCHENAI_LOCAL", default=True)

# Suppress specific warnings
warnings.filterwarnings("ignore", message="You are using deepeval version")

# Configure logging to reduce noise
logging.getLogger("litellm").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

# 1. Django Core Settings
# -----------------------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.0/ref/settings/


ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["*"] if DEBUG or KITCHENAI_LOCAL else ["localhost"],
    subcast=str,
)

ASGI_APPLICATION = "kitchenai.asgi.application"

# https://grantjenks.com/docs/diskcache/tutorial.html#djangocache
if "CACHE_LOCATION" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "diskcache.DjangoCache",
            "LOCATION": env.str("CACHE_LOCATION"),
            "TIMEOUT": 300,
            "SHARDS": 8,
            "DATABASE_TIMEOUT": 0.010,  # 10 milliseconds
            "OPTIONS": {"size_limit": 2**30},  # 1 gigabyte
        }
    }
elif env.bool("KITCHENAI_REDIS_CACHE", default=False):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env.str("REDIS_LOCATION", default="redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

CSRF_COOKIE_SECURE = not DEBUG

DATABASES = {
    "default": env.dj_db_url(
        "DATABASE_URL", default=f"sqlite:///{KITCHENAI_DB_DIR / 'db.sqlite3'}"
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False

if not DEBUG or KITCHENAI_LOCAL:
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL",
    default="example@example.com",
    validate=lambda v: Email()(parseaddr(v)[1]),
)

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "allauth_ui",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "compressor",
    "crispy_forms",
    "crispy_tailwind",
    "django_extensions",
    "django_htmx",
    "django_q",
    "django_q_registry",
    "django_tailwind_cli",
    "falco_toolbox",
    "health_check",
    "health_check.cache",
    "health_check.contrib.migrations",
    "health_check.db",
    "health_check.storage",
    "heroicons",
    "template_partials",
    "unique_user_email",
    "widget_tweaks",
    "slippers",
]

LOCAL_APPS = [
    "kitchenai.core",
    "kitchenai.notebooks",
    "kitchenai.bento",
    "kitchenai.plugins",
    "kitchenai.dashboard",
    # "kitchenai.django_webhook", # TODO: Uncomment this when we have a model to test with
]

if DEBUG:
    # Development only apps
    THIRD_PARTY_APPS = [
        "debug_toolbar",
        "whitenoise.runserver_nostatic",
        "django_browser_reload",
        "django_fastdev",
        "django_watchfiles",
        *THIRD_PARTY_APPS,
    ]

INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

if DEBUG or KITCHENAI_LOCAL:
    INTERNAL_IPS = [
        "127.0.0.1",
        "10.0.2.2",
    ]

LANGUAGE_CODE = "en-us"

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "plain_console": {
#             "format": "%(levelname)s %(message)s",
#         },
#         "verbose": {
#             "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
#         },
#     },
#     "handlers": {
#         "stdout": {
#             "class": "logging.StreamHandler",
#             "stream": sys.stdout,
#             # "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["stdout"],
#             "level": env.log_level("DJANGO_LOG_LEVEL", default="INFO"),
#         },
#         "kitchenai": {
#             "handlers": ["stdout"],
#             "level": env.log_level("KITCHENAI_LOG_LEVEL", default="INFO"),
#         },
#     },
# }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Set to INFO or WARNING to suppress DEBUG logs
            "propagate": True,
        },
        "urllib3.connectionpool": {
            "handlers": ["console"],
            "level": "WARNING",  # Suppress DEBUG logs from urllib3
            "propagate": False,
        },
        "chromadb": {
            "handlers": ["console"],
            "level": "WARNING",  # Suppress DEBUG logs from chromadb
            "propagate": False,
        },
        "kitchenai": {
            "handlers": ["console"],
            "level": env.log_level("KITCHENAI_LOG_LEVEL", default="DEBUG"),
            "propagate": False,  # Prevent propagation to the root logger
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",  # Set the root logger level
    },
}

MEDIA_ROOT = env.path("MEDIA_ROOT", default=APPS_DIR / "media")

MEDIA_URL = "/media/"

# https://docs.djangoproject.com/en/dev/topics/http/middleware/
# https://docs.djangoproject.com/en/dev/ref/middleware/#middleware-ordering
MIDDLEWARE = [
    # Cache middleware - commented out to prevent unwanted caching
    # "django.middleware.cache.UpdateCacheMiddleware",  # Cache middleware start
    
    # Standard middleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "kitchenai.core.middleware.HtmxNoCacheMiddleware",
    
    # Cache middleware end - commented out
    # "django.middleware.cache.FetchFromCacheMiddleware",
]

# if DEBUG or KITCHENAI_LOCAL:
#     MIDDLEWARE.remove("django.middleware.cache.UpdateCacheMiddleware")
#     MIDDLEWARE.remove("django.middleware.cache.FetchFromCacheMiddleware")

if DEBUG:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.common.CommonMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

ROOT_URLCONF = "kitchenai.urls"

SECRET_KEY = env.str(
    "SECRET_KEY", default="django-insecure-ef6nIh7LcUjPtixFdz0_aXyUwlKqvBdJEcycRR6RvRY"
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = not (DEBUG or KITCHENAI_LOCAL)

SECURE_HSTS_PRELOAD = not (DEBUG or KITCHENAI_LOCAL)

# https://docs.djangoproject.com/en/dev/ref/middleware/#http-strict-transport-security
# 2 minutes to start with, will increase as HSTS is tested
# example of production value: 60 * 60 * 24 * 7 = 604800 (1 week)
SECURE_HSTS_SECONDS = (
    0 if DEBUG or KITCHENAI_LOCAL else env.int("SECURE_HSTS_SECONDS", default=60 * 2)
)

# https://noumenal.es/notes/til/django/csrf-trusted-origins/
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURE_SSL_REDIRECT = not DEBUG

SERVER_EMAIL = env.str(
    "SERVER_EMAIL",
    default=DEFAULT_FROM_EMAIL,
    validate=lambda v: Email()(parseaddr(v)[1]),
)

SESSION_COOKIE_SECURE = not (DEBUG or KITCHENAI_LOCAL)

# S3/MinIO Storage Settings
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env.str("AWS_ACCESS_KEY_ID", default=None),
            "secret_key": env.str("AWS_SECRET_ACCESS_KEY", default=None),
            "bucket_name": env.str("AWS_STORAGE_BUCKET_NAME", default=None),
            "endpoint_url": env.str("AWS_S3_ENDPOINT_URL", default=None),
            "region_name": env.str("AWS_DEFAULT_REGION", default="us-east-1"),
            "verify": env.bool("AWS_S3_VERIFY", default=False),
            "addressing_style": env.str("AWS_S3_ADDRESSING_STYLE", default="path"),
            "use_ssl": env.bool("AWS_S3_USE_SSL", default=False),
        },
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedStaticFilesStorage"
        ),
    },
}

# Only use local storage if not using S3 and in debug/local mode
if (DEBUG or KITCHENAI_LOCAL) and not env.bool("USE_S3", default=False):
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }

# https://nickjanetakis.com/blog/django-4-1-html-templates-are-cached-by-default-with-debug-true
DEFAULT_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

CACHED_LOADERS = [("django.template.loaders.cached.Loader", DEFAULT_LOADERS)]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "kitchenai.context_processors.theme_context",
                "kitchenai.context_processors.version_context",
                "kitchenai.context_processors.local_context",
            ],
            "builtins": [
                "template_partials.templatetags.partials",
                "heroicons.templatetags.heroicons",
            ],
            "debug": DEBUG,
            "loaders": [
                (
                    "template_partials.loader.Loader",
                    DEFAULT_LOADERS if (DEBUG or KITCHENAI_LOCAL) else CACHED_LOADERS,
                )
            ],
        },
    },
]

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = True

WSGI_APPLICATION = "kitchenai.wsgi.application"

# 2. Django Contrib Settings
# -----------------------------------------------------------------------------------------------

# django.contrib.auth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
if DEBUG or KITCHENAI_LOCAL:
    AUTH_PASSWORD_VALIDATORS = []

# django.contrib.staticfiles
STATIC_ROOT = APPS_DIR / "staticfiles"

STATIC_URL = "/static/"

# STATICFILES_DIRS = [APPS_DIR / "static"] if DEBUG else []
STATICFILES_DIRS = [APPS_DIR / "static"]


STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# 3. Third Party Settings
# -------------------------------------------------------------------------------------------------

# django-allauth
ACCOUNT_AUTHENTICATION_METHOD = "email"

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if (DEBUG or KITCHENAI_LOCAL) else "https"

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_LOGOUT_REDIRECT_URL = "account_login"

ACCOUNT_SESSION_REMEMBER = True

ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False

ACCOUNT_UNIQUE_EMAIL = True

# Forms and UI
ACCOUNT_FORMS = {
    'login': 'allauth.account.forms.LoginForm',

}

LOGIN_REDIRECT_URL = "dashboard:home"


# django-anymail
if not (DEBUG or KITCHENAI_LOCAL):
    resend_api_key = env.str("RESEND_API_KEY", default=None)
    if resend_api_key:
        ANYMAIL = {
            "RESEND_API_KEY": resend_api_key,
        }
    else:
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# django-compressor
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = not DEBUG

COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
        "refreshcss.filters.RefreshCSSFilter",
    ],
    "js": ["compressor.filters.jsmin.rJSMinFilter"],
}

# django-crispy-forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

# django-debug-toolbar
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_COLLAPSED": True,
    "UPDATE_ON_FETCH": True,
    "ROOT_TAG_EXTRA_ATTRS": "hx-preserve",
}

# django-q2
Q_CLUSTER = {
    "name": "ORM",
    "workers": multiprocessing.cpu_count() * 2 + 1,
    "timeout": 60 * 10,  # 10 minutes
    "retry": 60 * 12,  # 12 minutes
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

# sentry
if env.bool("KITCHENAI_SENTRY", default=False):
    if (SENTRY_DSN := env.url("SENTRY_DSN", default=None)).scheme and not (
        DEBUG or KITCHENAI_LOCAL
    ):
        sentry_sdk.init(
            dsn=SENTRY_DSN.geturl(),
            environment=env.str(
                "SENTRY_ENV",
                default="development",
                validate=OneOf(["development", "production"]),
            ),
            integrations=[
                DjangoIntegration(),
                LoggingIntegration(event_level=None, level=None),
            ],
            traces_sampler=sentry_traces_sampler,
            profiles_sampler=sentry_profiles_sampler,
            send_default_pii=True,
        )

# 4. Project Settings
# -----------------------------------------------------------------------------------------------------

ADMIN_URL = env.str("ADMIN_URL", default="kitchenai-admin/")


# KITCHEN AI
KITCHENAI_LLM_PROVIDER = env.str("KITCHENAI_LLM_PROVIDER", default="openai")
KITCHENAI_LLM_MODEL = env.str("KITCHENAI_LLM_MODEL", default="gpt-4o")

#main kitchenai settings
KITCHENAI = {
    "bento": [],
    "plugins": [],
    "apps": [],
    "settings": {
        "auth": env.bool("KITCHENAI_AUTH", default=False),
    },
}

KITCHENAI_JWT_SECRET = env.str("KITCHENAI_JWT_SECRET", default="")

KITCHENAI_APP = "bento"

# Theme settings
KITCHENAI_THEMES = [
    "cupcake",    # Light, cute
    "dark",       # Dark mode
    "light",      # Light mode
    "dracula",    # Dark purple
    "night",      # Dark blue
    "winter",     # Light blue
    "forest",     # Dark green
    "sunset",     # Orange/pink
    "business",   # Professional light
    "cyberpunk",  # Neon
    "synthwave",  # Retro dark
    "retro",      # Vintage light
    "valentine",  # Pink theme
    "garden",
    "wireframe",    # Nature green
    "aqua",       # Light blue
]

# Default theme (can be overridden by env var)
KITCHENAI_THEME = env.str("KITCHENAI_THEME", default="winter")

# Validate theme setting
if KITCHENAI_THEME not in KITCHENAI_THEMES:
    KITCHENAI_THEME = "cupcake"  # Fallback to default if invalid theme specified

# WEBHOOKS
# DJANGO_WEBHOOK = dict(MODELS=["core.TestObject"])

# Django plugin system. This has to be the last line
djp.settings(globals())
