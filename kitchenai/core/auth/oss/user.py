
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import logging
from kitchenai.core.auth.user import KitchenAIUser

logger = logging.getLogger(__name__)


class OSSUser(KitchenAIUser):
    """Custom user model with additional functionality"""


    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    

    def can_create_project(self) -> bool:
        """
        Example method that we want to call from the rest of the code.
        The Cloud version might override it with plan-based logic,
        the OSS version might return True unconditionally.
        """
        raise True
    