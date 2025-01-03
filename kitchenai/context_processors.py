from django.conf import settings

def theme_context(request):
    return {
        'KITCHENAI_THEME': getattr(settings, 'KITCHENAI_THEME', 'cupcake')
    } 