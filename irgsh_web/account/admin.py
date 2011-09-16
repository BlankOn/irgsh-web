from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    def can_submit(user):
        return user.has_perm('build.specification_submit')
    can_submit.boolean = True

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', can_submit)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

