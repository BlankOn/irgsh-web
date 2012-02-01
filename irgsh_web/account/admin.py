from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class CustomUserAdmin(UserAdmin):
    def can_submit(user):
        return user.has_perm('build.specification_submit')
    can_submit.boolean = True

    def twitter(user):
        account = user.get_profile().twitter
        if account:
            return '@%s' % account
        return ''

    inlines = [UserProfileInline,]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', can_submit, twitter)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

