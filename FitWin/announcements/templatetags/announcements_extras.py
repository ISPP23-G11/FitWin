from django import template
from django.http import QueryDict

register = template.Library()


@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)


@register.filter
def remove_duplicated_get_params(query_string):
    query_params = QueryDict(query_string, mutable=True)
    query_params_filtered = QueryDict('', mutable=True)
    query_params_filtered.update(query_params.dict())
    return query_params_filtered.urlencode()
