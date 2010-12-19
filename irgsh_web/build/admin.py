from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Architecture, Distribution, Builder, Specification

class ArchitectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'active',)

class DistributionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'mirror', 'dist', 'components',)

    fieldsets = (
        (None, {
            'fields': ('name', 'mirror', 'dist', 'components', 'active', 'extra',)
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
            'fields': ('name', 'architecture', 'active', 'location', 'last_activity',),
        }),
    )

class SpecificationAdmin(admin.ModelAdmin):
    def orig(obj):
        return obj.orig is not None
    orig.short_description = _('Has Orig')
    
    def source_package(obj):
        if obj.source_package is None:
            return _('Unknown')
        return obj.source_package.name
    orig.short_description = _('Source Package')

    list_display = ('distribution', 'submitter', source_package,
                    'source', 'source_type', orig, 'created',)

    fieldsets = (
        (None, {
            'fields': ('distribution', 'submitter',)
        }),
        ('Source', {
            'fields': ('source', 'source_type', 'orig',),
        }),
        ('Package', {
            'fields': ('source_package',)
        }),
    )

admin.site.register(Architecture, ArchitectureAdmin)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Builder, BuilderAdmin)
admin.site.register(Specification, SpecificationAdmin)

