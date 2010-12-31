from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Distribution, Builder, Specification

class DistributionAdmin(admin.ModelAdmin):
    list_display = ('repo', 'active', 'mirror', 'dist', 'components',)

    fieldsets = (
        (None, {
            'fields': ('repo', 'mirror', 'dist', 'components', 'active', 'extra',)
        }),
    )

class BuilderAdmin(admin.ModelAdmin):
    def last_activity(obj):
        if obj.last_activity is None:
            return _('Unknown')
        return obj.last_activity
    last_activity.short_description = _('Last Activity')

    list_display = ('name', 'active', 'architecture', 'location', last_activity,)

    fieldsets = (
        (None, {
            'fields': ('name', 'architecture', 'active', 'last_activity', 'location', 'remark',),
        }),
    )

class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('distribution', 'submitter', 'status',
                    'package', 'version',
                    'created',)

    fieldsets = (
        (None, {
            'fields': ('distribution', 'submitter', 'created',)
        }),
        ('Source', {
            'fields': ('source', 'source_type', 'orig',),
        }),
        ('Package', {
            'fields': ('package', 'version',)
        }),
    )

admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Builder, BuilderAdmin)
admin.site.register(Specification, SpecificationAdmin)

