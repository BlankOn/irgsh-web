from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Architecture, Distribution, Component, Package, \
                    PackageDistribution

class DistributionAdmin(admin.ModelAdmin):
    def architectures(obj):
        archs = obj.architectures.all().values_list('name', flat=True)
        return ', '.join(archs)

    def components(obj):
        archs = obj.components.all().values_list('name', flat=True)
        return ', '.join(archs)

    list_display = ('name', 'active', architectures, components)

class PackageDistributionInline(admin.TabularInline):
    model = PackageDistribution
    extra = 1

class PackageAdmin(admin.ModelAdmin):
    def distributions(obj):
        return ', '.join(map(str, PackageDistribution.objects.filter(package=obj)))

    list_display = ('name', distributions,)
    inlines = [PackageDistributionInline]

admin.site.register(Architecture)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Component)
admin.site.register(Package, PackageAdmin)

