from datetime import datetime

from django import template

register = template.Library()

@register.filter(expects_localtime=True)
def str_to_datetime(value, arg="%Y-%m-%dT%H:%M:%S.%fZ"):
    return datetime.strptime(value, arg)
