from django import template
from setup import get_version
register = template.Library()

@register.filter
def get_version():
    return get_version()
