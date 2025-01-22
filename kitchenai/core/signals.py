from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

User = get_user_model()


@receiver(post_save, sender=settings.AUTH_ORGANIZATIONMEMBER_MODEL)
@receiver(post_delete, sender=settings.AUTH_ORGANIZATIONMEMBER_MODEL)
def invalidate_user_org_cache(sender, instance, **kwargs):
    cache_key = f"user_org_{instance.user.id}"
    cache.delete(cache_key)
