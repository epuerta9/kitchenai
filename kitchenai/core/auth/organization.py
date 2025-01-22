from django.db import models
from django.conf import settings
from falco_toolbox.models import TimeStamped


class Organization(TimeStamped):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class OrganizationMember(TimeStamped):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    class Meta:
        abstract = True
        unique_together = ('organization', 'user')

class SignupRequest(TimeStamped):
    organization = models.ForeignKey(settings.AUTH_ORGANIZATION_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_signups'
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_signups'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Signup request from {self.email} for {self.organization}"
