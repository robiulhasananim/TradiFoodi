from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, BuyerProfile

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'role', 'is_staff', 'is_superuser', 'is_verified')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_verified')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password1', 'password2', 'is_verified', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'postal_code')
    search_fields = ('user__username', 'user__email')
    list_filter = ('city',)

admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile, BuyerProfileAdmin)
