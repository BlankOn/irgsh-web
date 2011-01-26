from django.contrib import admin
from django import forms
from django.utils.translation import ugettext as _

from .models import Distribution, Builder, Specification, BuildTask, Worker
from . import utils

class DistributionAdmin(admin.ModelAdmin):
    list_display = ('repo', 'active', 'mirror', 'dist', 'components',)

    fieldsets = (
        (None, {
            'fields': ('repo', 'mirror', 'dist', 'components', 'active', 'extra',)
        }),
    )

class BuilderAdminForm(forms.ModelForm):
    class Meta:
        model = Builder

    def clean_cert_subject(self):
        cert_subject = self.cleaned_data['cert_subject']
        return utils.make_canonical(cert_subject)

class BuilderAdmin(admin.ModelAdmin):
    def last_activity(obj):
        if obj.last_activity is None:
            return _('Unknown')
        return obj.last_activity
    last_activity.short_description = _('Last Activity')

    list_display = ('name', 'active', 'architecture', 'location', last_activity,)

    fieldsets = (
        (None, {
            'fields': ('name', 'architecture', 'cert_subject',
                       'active', 'location', 'remark', 'last_activity',),
        }),
    )

    form = BuilderAdminForm

class WorkerAdminForm(forms.ModelForm):
    class Meta:
        model = Worker

    def clean_cert_subject(self):
        cert_subject = self.cleaned_data['cert_subject']
        return utils.make_canonical(cert_subject)

class WorkerAdmin(admin.ModelAdmin):
    def last_activity(obj):
        if obj.last_activity is None:
            return _('Unknown')
        return obj.last_activity
    last_activity.short_description = _('Last Activity')

    list_display = ('name', 'type', 'active', last_activity,)

    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'cert_subject', 'active', 'last_activity',),
        }),
    )

    form = WorkerAdminForm

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
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Specification, SpecificationAdmin)
admin.site.register(BuildTask, BuildTaskAdmin)

