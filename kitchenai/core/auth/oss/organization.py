from django.db import models
from kitchenai.core.auth.organization import Organization, OrganizationMember
from kitchenai.core.auth.oss.user import OSSUser
from kitchenai.bento.models import RemoteClient

class OSSOrganization(Organization):

    DEFAULT_NAME = "Default Organization"

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    allow_signups = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class OSSOrganizationMember(OrganizationMember):
    organization = models.ForeignKey(OSSOrganization, on_delete=models.CASCADE)
    user = models.ForeignKey(OSSUser, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)


    class Meta:
        unique_together = ('organization', 'user')

        

class OSSBentoClient(RemoteClient):
    organization = models.ForeignKey(OSSOrganization, on_delete=models.CASCADE)
