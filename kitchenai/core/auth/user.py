from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class KitchenAIUser(AbstractUser):
    """Custom user model with additional functionality"""

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = True
    
    # Make email required and unique
    email = models.EmailField('email address', unique=True)
    
    # Role choices
    ROLE_ADMIN = 'admin'
    ROLE_DEVELOPER = 'developer'
    ROLE_VIEWER = 'viewer'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_DEVELOPER, 'Developer'),
        (ROLE_VIEWER, 'Viewer'),
    ]
    
    role = models.CharField(
        max_length=255,
        choices=ROLE_CHOICES,
        default=ROLE_VIEWER,
        blank=True
    )
    is_onboarding_complete = models.BooleanField(default=False)

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Email is automatically required

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
        
        if is_new:
            self.create_organization()

    def can_create_project(self) -> bool:
        """
        Example method that we want to call from the rest of the code.
        The Cloud version might override it with plan-based logic,
        the OSS version might return True unconditionally.
        """
        raise NotImplementedError("Implement in concrete subclass")

    def create_organization(self):
        """Create default organization for new user"""
        from django.apps import apps
        from django.conf import settings
        Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
        OrganizationMember = apps.get_model(settings.AUTH_ORGANIZATIONMEMBER_MODEL)
        if settings.KITCHENAI_LICENSE == 'oss':
            #Default organization is created in the apps.py file
            #attach the user to the default organization
            default_organization = Organization.objects.get(slug="default-organization")

            #check to see if there are any organization members. If there are none, make the user an admin
            if not OrganizationMember.objects.exists():
                OrganizationMember.objects.create(
                    organization=default_organization,
                    user=self,
                    is_admin=True
                )
            else:
                #if there are organization members, add the user to the organization
                OrganizationMember.objects.create(
                    organization=default_organization,
                    user=self,
                    is_admin=False
                )

            self.organization = default_organization
            self.save()
            return
