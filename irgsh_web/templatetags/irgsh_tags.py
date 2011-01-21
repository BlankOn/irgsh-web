from datetime import datetime, timedelta

from django import template
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

def datetime_and_age(value):
    if not isinstance(value, datetime):
        return value
    res = [value.strftime(_('%A, %d %B %Y %H:%M:%S'))]

    now = datetime.now()
    delta = now - value
    if delta.days == 1:
        res.append(_('(%(day)s day ago)') % {'day': delta.days})
    elif 1 < delta.days <= 7:
        res.append(_('(%(days)s days ago)') % {'days': delta.days})
    elif delta.seconds >= 7200:
        res.append(_('(%(hours)s hours ago)') % {'hours': delta.seconds // 3600})
    elif delta.seconds >= 3600:
        res.append(_('(%(hour)s hour ago)') % {'hour': delta.seconds // 3600})
    elif delta.seconds >= 120:
        res.append(_('(%(mins)s mins ago)') % {'mins': delta.seconds // 60})
    elif delta.seconds >= 60:
        res.append(_('(%(min)s min ago)') % {'min': delta.seconds // 60})
    elif delta.seconds:
        res.append(_('(just now)'))

    return ' '.join(res)

def since(now, start):
    if not isinstance(now, datetime) or not isinstance(start, datetime):
        return value

    delta = now - start
    if delta.days < 0 or delta.seconds < 0:
        return ''
    elif delta.days > 1:
        return _('%(days)s days' % {'days': delta.days})
    elif delta.days >= 1:
        return _('%(day)s day' % {'day': delta.days})
    elif delta.seconds >= 7200:
        return _('%(hours)s hours') % {'hours': delta.seconds // 3600}
    elif delta.seconds >= 7200:
        return _('%(hour)s hour') % {'hour': delta.seconds // 3600}
    elif delta.seconds >= 120:
        return _('%(mins)s mins') % {'mins': delta.seconds // 60}
    elif delta.seconds >= 60:
        return _('%(min)s min') % {'min': delta.seconds // 60}
    elif delta.seconds > 1:
        return _('%(secs)s secs') % {'secs': delta.seconds}
    else:
        return _('%(sec)s sec') % {'sec': int(delta.seconds)}

def datetime_and_since(value, start):
    if not isinstance(value, datetime) or not isinstance(start, datetime):
        return value

    res = [value.strftime(_('%A, %d %B %Y %H:%M:%S'))]

    delta = value - start
    if delta.days <= 7:
        res.append('(+%s)' % since(value, start))

    return ' '.join(res)

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
        return value.strftime(_('%d/%m %h:%m'))
    else:
        return value.strftime(_('%d/%m/%y %h:%m'))

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

def datetime_relative(value, target):
    if value.date() == target.date():
        return value.strftime('%H:%M')
    elif value.year == target.year:
        return value.strftime('%d/%m %H:%M')
    return value.strftime('%d/%m/%y %H:%M')

def collapsible_changelog(changelog):
    lines = changelog.splitlines()
    first = conditional_escape(lines[0])
    rest = conditional_escape('\n'.join(lines[1:]))
    html = '<pre onclick="toggle_next(this);">%s</pre><pre style="display:none">\n%s</pre>' % \
            (first, rest)
    return mark_safe(html)

def filesize(size):
    try:
        size = float(size)
    except ValueError:
        return size

    units = ['B', 'KiB', 'MiB', 'GiB']
    for unit in units:
        if size < 1024:
            break
        size = size / 1024
    return '%.2f %s' % (size, unit)


register = template.Library()
register.filter('datetime_or_age', datetime_or_age)
register.filter('full_datetime_or_age', full_datetime_or_age)
register.filter('datetime_and_age', datetime_and_age)
register.filter('datetime_and_since', datetime_and_since)
register.filter('since', since)
register.filter('datetime_relative', datetime_relative)
register.filter('collapsible_changelog', collapsible_changelog)
register.filter('filesize', filesize)

