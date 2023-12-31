from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from twitter.accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'avatar', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profiles'


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    date_hierarchy = 'date_joined'
    inlines = (UserProfileInline,)


# Unregister UserAdmin (imported as BaseUserAdmin) that's registered by Django
admin.site.unregister(User)
# Register the customized UserAdmin
admin.site.register(User, UserAdmin)