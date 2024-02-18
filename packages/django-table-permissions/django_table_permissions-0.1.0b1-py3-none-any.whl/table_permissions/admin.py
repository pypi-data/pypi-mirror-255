from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Group
from django.contrib.auth.admin import GroupAdmin as DjGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin
from django.core.exceptions import ImproperlyConfigured

from table_permissions import app_settings
from table_permissions.widgets import TabularPermissionsWidget


User = get_user_model()


class UserTabularPermissionsMixin:

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "user_permissions":
            field.widget = TabularPermissionsWidget(
                db_field.verbose_name, db_field.name in self.filter_vertical
            )
            field.help_text = ""
        return field


class GroupTabularPermissionsMixin:
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "permissions":
            field.widget = TabularPermissionsWidget(
                db_field.verbose_name,
                db_field.name in self.filter_vertical,
                "permissions",
            )
            field.help_text = ""
        return field


try:
    UserAdminModel = admin.site._registry[User].__class__
except:  # noqa: E722
    UserAdminModel = DjUserAdmin

try:
    GroupAdminModel = admin.site._registry[Group].__class__
except:  # noqa: E722
    GroupAdminModel = DjGroupAdmin


class TabularPermissionsUserAdmin(UserTabularPermissionsMixin, UserAdminModel):
    pass


class TabularPermissionsGroupAdmin(GroupTabularPermissionsMixin, GroupAdminModel):
    pass


if app_settings.AUTO_IMPLEMENT:
    try:
        admin.site.unregister(User)
        admin.site.register(User, TabularPermissionsUserAdmin)
        admin.site.unregister(Group)
        admin.site.register(Group, TabularPermissionsGroupAdmin)

    except:  # noqa: E722
        raise ImproperlyConfigured(
            "Please make sure that django.contrib.auth (Or the app containing your custom User model) "
            "comes before tabular_permissions in INSTALLED_APPS; Or set AUTO_IMPLEMENT to False in your settings."
        )
