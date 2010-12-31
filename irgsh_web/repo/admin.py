from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Architecture, Distribution, Component, Package

class DistributionAdmin(admin.ModelAdmin):
    def architectures(obj):
        archs = obj.architectures.all().values_list('name', flat=True)
        return ', '.join(archs)

    list_display = ('name', 'active', architectures,)

class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'distribution',)

class PackageAdmin(admin.ModelAdmin):
    def component(obj):
        return obj.component.name
    component.admin_order_field = 'component__name'

    def distribution(obj):
        return obj.component.distribution.name
    distribution.admin_order_field = 'component__distribution__name'

    list_display = ('name', component, distribution,)

admin.site.register(Architecture)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Package, PackageAdmin)

