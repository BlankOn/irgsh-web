from jobs.models import * 
from django.contrib import admin


class TaskInline(admin.StackedInline):
    model = Task
    max_num = 1

class JobAdmin(admin.ModelAdmin):
    inlines = [TaskInline,]

admin.site.register(Architecture)
admin.site.register(Builder)
admin.site.register(Job, JobAdmin)
admin.site.register(Distribution)
admin.site.register(HandlerAdministrator)
