from django import template
#from setup import get_version
register = template.Library()

@register.simple_tag
def get_version():
    return "0.2.blahblah"
