from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Distribution, Builder, Specification, BuildTask

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
    def specification_id(obj):
        return str(obj.id)
    specification_id.short_description = _('spec id')
    specification_id.admin_order_field = 'id'

    list_display = (specification_id, 'distribution', 'submitter', 'status',
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

class BuildTaskAdmin(admin.ModelAdmin):
    def specification_id(obj):
        return str(obj.specification.id)
    specification_id.short_description = _('spec id')
    specification_id.admin_order_field = 'specification__id'

    list_display = (specification_id, 'architecture', 'task_id',
                    'created', 'updated',
                    'status', 'builder',)

admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Builder, BuilderAdmin)
admin.site.register(Specification, SpecificationAdmin)
admin.site.register(BuildTask, BuildTaskAdmin)

