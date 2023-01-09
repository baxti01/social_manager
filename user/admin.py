from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from user.forms import UserChangeForm, UserCreationForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff',)
    list_display_links = ['id', 'email']
    # fieldsets = BaseUserAdmin.fieldsets
    readonly_fields = ['date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'date_joined', 'is_active')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    # filter_horizontal = ()


admin.site.register(get_user_model(), UserAdmin)
admin.site.unregister(Group)
