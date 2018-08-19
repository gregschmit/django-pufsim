from django import template
register = template.Library()

@register.filter
def get_attr(obj, param):
    """
    `getattr` template tag implementation.
    """
    return getattr(obj, param, None)

@register.filter
def split_by(value, sep):
    return value.split(sep)

@register.filter
def index(value, i):
    return value[i]
