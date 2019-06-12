from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
@stringfilter
def title_case_proper(value):
    return ' '.join([x[0].upper() + x[1:] for x in value.split()])
