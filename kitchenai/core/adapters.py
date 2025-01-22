from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.apps import apps
from kitchenai.core.auth.organization import SignupRequest

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
    # def save_user(self, request, user, form, commit=True):
    #     user = super().save_user(request, user, form, commit=False)
        
    #     # If organization requires approval
    #     if settings.KITCHENAI_LICENSE == 'oss':
    #         # add sign up request to the default organization

    #         org_slug = 'default-organization'
    #         if org_slug:
    #             org = get_object_or_404(Organization, slug=org_slug)
    #         if org.require_approval:
    #             user.is_active = False  # Deactivate user until approved
    #             SignupRequest.objects.create(
    #                 organization=org,
    #                 email=user.email,
    #                 first_name=user.first_name,
    #                 last_name=user.last_name,
    #                 is_approved=False,
    #                 is_rejected=False,
    #                 approved_by=None,
    #                 rejected_by=None,
    #                 notes=''
    #             )
    #     return user
        # org_slug = request.GET.get('org')
        # if org_slug:
        #     org = get_object_or_404(Organization, slug=org_slug)
        # if org.require_approval:
        #     user.is_active = False  # Deactivate user until approved
        #     SignupRequest.objects.create(
        #         organization=org,
        #         email=user.email,
        #         first_name=user.first_name,
        #         last_name=user.last_name,
        #         is_approved=False,
        #         is_rejected=False,
        #         approved_by=None,
        #         rejected_by=None,
        #         notes=''
        #     )
                
        # if commit:
        #     user.save()
        # return user