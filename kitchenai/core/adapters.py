from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.apps import apps

Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)

class KitchenAIAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Check if global registration is enabled
        if not getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True):
            return False
            
        # If organization slug is provided in request
        org_slug = request.GET.get('org')
        if org_slug:
            try:
                org = Organization.objects.get(slug=org_slug)
                return org.allow_signups
            except Organization.DoesNotExist:
                return False
                
        return True