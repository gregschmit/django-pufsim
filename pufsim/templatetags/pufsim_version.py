from django import template
from pufsim import _version
register = template.Library()

@register.simple_tag
def get_version():
    return _version.get_version()
