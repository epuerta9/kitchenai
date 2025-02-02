
from functools import wraps
from django.conf import settings
from django.contrib.auth.decorators import login_required

def optional_login_required(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        # Check if anonymous plugin use is allowed in settings
        allow_anonymous = getattr(settings, 'KITCHENAI', {}).get('ALLOW_ANONYMOUS_PLUGINS', False)
        
        if allow_anonymous:
            return await view_func(request, *args, **kwargs)
        else:
            # If anonymous not allowed, use the standard login_required
            return login_required(view_func)(request, *args, **kwargs)
    
    return _wrapped_view