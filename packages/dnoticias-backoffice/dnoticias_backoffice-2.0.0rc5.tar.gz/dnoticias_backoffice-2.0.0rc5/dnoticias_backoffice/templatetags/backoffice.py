from django import template

from dnoticias_backoffice.utils import get_acronym

register = template.Library()


@register.filter
def acronym(user):
    return get_acronym(user)


@register.simple_tag
def get(_dict, key):
    return _dict.get(key, '')
