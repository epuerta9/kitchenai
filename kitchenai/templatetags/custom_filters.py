from django import template

register = template.Library()

@register.filter
def contains(value, substring):
    """Check if a string contains a given substring."""
    return substring in value
