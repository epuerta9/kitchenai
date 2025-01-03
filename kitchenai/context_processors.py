from django.conf import settings
from kitchenai import __version__ as VERSION
def theme_context(request):
    return {
        'KITCHENAI_THEME': getattr(settings, 'KITCHENAI_THEME', 'cupcake')
    } 

def version_context(request):
    return {
        'VERSION': VERSION
    }