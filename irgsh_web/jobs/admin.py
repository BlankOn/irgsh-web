from jobs.models import * 
from django.contrib import admin

class AdministratorInline(admin.StackedInline):
    model = BuilderAdministrator
    max_num = 5

class AdministratorAdmin(admin.ModelAdmin):
    inlines = [AdministratorInline,] 

class DistributionInline(admin.StackedInline):
    model = DistributionArchitecture

class DistributionAdmin(admin.ModelAdmin):
    inlines = [DistributionInline,]

class TaskInline(admin.StackedInline):
    model = Task
    max_num = 1

class JobAdmin(admin.ModelAdmin):
    inlines = [TaskInline,]

admin.site.register(Architecture)
admin.site.register(Component)
admin.site.register(Package)
admin.site.register(Builder,AdministratorAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Distribution, DistributionAdmin)
