from django import template
from pufsim import version
register = template.Library()

@register.simple_tag
def get_version():
    return version.get_version()
