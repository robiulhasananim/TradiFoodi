from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserModelAdmin(BaseUserAdmin):
    list_display = ('uid', 'email', 'first_name', 'last_name', 'phone', 'role', 'city', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_superuser', 'is_active', 'city')
    search_fields = ('uid', 'email', 'first_name', 'last_name', 'phone', 'city')
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'role')}),
        ('Address Details', {'fields': ('address', 'city', 'postal_code')}),
        ('Permissions', {'fields': ('is_superuser', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone', 'role', 
                'address', 'city', 'postal_code', 'avatar',
                'password', 'is_superuser', 'is_active'
            ),
        }),
    )

# Register
admin.site.register(User, UserModelAdmin)
