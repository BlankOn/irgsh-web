from datetime import datetime, timedelta

from django import template
from django.utils.translation import ugettext as _

def datetime_or_age(value):
    if not isinstance(value, datetime):
        return value
    now = datetime.now()
    delta = now - value

    if delta < timedelta(seconds=60):
        return _('%(seconds)d sec ago') % {'seconds': delta.seconds}
    elif delta < timedelta(seconds=3600):
        return _('%(minutes)d min ago') % {'minutes': (delta.seconds // 60)}
    elif value.date() == now.date():
        return _('%(hour)02d:%(minute)02d') % \
               {'hour': value.hour, 'minute': value.minute}
    elif value.year == now.year:
        return value.strftime(_('%d/%m %H:%M'))
    else:
        return value.strftime(_('%d/%m/%y %H:%M'))

def full_datetime_or_age(value):
    if not isinstance(value, datetime):
        return value
    now = datetime.now()
    delta = now - value

    if delta < timedelta(seconds=60):
        return _('%(seconds)d sec ago') % {'seconds': delta.seconds}
    elif delta < timedelta(seconds=3600):
        return _('%(minutes)d min ago') % {'minutes': (delta.seconds // 60)}
    elif value.date() == now.date():
        return _('today at %(hour)02d:%(minute)02d') % \
               {'hour': value.hour, 'minute': value.minute}
    elif value.year == now.year:
        return value.strftime(_('%a, %d/%m %H:%M'))
    else:
        return value.strftime(_('%d/%m/%y %H:%M'))

register = template.Library()
register.filter('datetime_or_age', datetime_or_age)
register.filter('full_datetime_or_age', full_datetime_or_age)

