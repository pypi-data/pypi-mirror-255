from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import Group
from django.contrib.auth.admin import GroupAdmin as DjGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin
from django.core.exceptions import ImproperlyConfigured

from table_permissions import app_settings
from table_permissions.widgets import TablePermissionsWidget


User = get_user_model()


class UserTablePermissionsMixin:

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "user_permissions":
            field.widget = TablePermissionsWidget(
                db_field.verbose_name, db_field.name in self.filter_vertical
            )
            field.help_text = ""
        return field


class GroupTablePermissionsMixin:
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "permissions":
            field.widget = TablePermissionsWidget(
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


class TablePermissionsUserAdmin(UserTablePermissionsMixin, UserAdminModel):
    pass


class TablePermissionsGroupAdmin(GroupTablePermissionsMixin, GroupAdminModel):
    pass


if app_settings.AUTO_IMPLEMENT:
    try:
        admin.site.unregister(User)
        admin.site.register(User, TablePermissionsUserAdmin)
        admin.site.unregister(Group)
        admin.site.register(Group, TablePermissionsGroupAdmin)

    except:  # noqa: E722
        raise ImproperlyConfigured(
            "Please make sure that django.contrib.auth (Or the app containing your custom User model) "
            "comes before table_permissions in INSTALLED_APPS; Or set AUTO_IMPLEMENT to False in your settings."
        )
