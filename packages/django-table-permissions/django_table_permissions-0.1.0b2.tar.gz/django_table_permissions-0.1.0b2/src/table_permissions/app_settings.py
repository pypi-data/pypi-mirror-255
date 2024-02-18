from django.conf import settings
from django.utils.module_loading import import_string


TABLE_PERMISSIONS_CONFIG = {
    "template": "table_permissions/admin/table_permissions.html",
    "js_file": "table_permissions/table_permissions.js",
    "exclude": {
        "override": False,
        "apps": [],
        "models": [],
        "function": "table_permissions.helpers.dummy_permissions_exclude",
    },
    "auto_implement": True,
    "use_for_concrete": False,
    "custom_permission_translation": "table_permissions.helpers.custom_permissions_translator",
    "apps_customization_func": "table_permissions.helpers.apps_customization_func",
    "custom_permissions_customization_func": "table_permissions.helpers.custom_permissions_customization_func",
}
user_conf = getattr(settings, "TABLE_PERMISSIONS_CONFIG", False)

if user_conf:
    # we update the exclude dict first
    TABLE_PERMISSIONS_CONFIG["exclude"].update(user_conf.get("exclude", {}))
    user_conf["exclude"] = TABLE_PERMISSIONS_CONFIG["exclude"]
    # update the rest if the configuration
    TABLE_PERMISSIONS_CONFIG.update(user_conf)

AUTO_IMPLEMENT = TABLE_PERMISSIONS_CONFIG["auto_implement"]
TEMPLATE = TABLE_PERMISSIONS_CONFIG["template"]
JS_FILE = TABLE_PERMISSIONS_CONFIG["js_file"]

_base_exclude_apps = ["sessions", "contenttypes", "admin"]
user_exclude = TABLE_PERMISSIONS_CONFIG["exclude"]
if not user_exclude.get("override", False):
    EXCLUDE_APPS = _base_exclude_apps + user_exclude.get("apps", [])
else:
    EXCLUDE_APPS = user_exclude.get("apps", [])
EXCLUDE_APPS = [x.lower() for x in EXCLUDE_APPS]

EXCLUDE_MODELS = user_exclude.get("models", [])
EXCLUDE_MODELS = [x.lower() for x in EXCLUDE_MODELS]

model_exclude_func = user_exclude.get("function")
EXCLUDE_FUNCTION = import_string(model_exclude_func)

USE_FOR_CONCRETE = TABLE_PERMISSIONS_CONFIG["use_for_concrete"]
TRANSLATION_FUNC = import_string(
    TABLE_PERMISSIONS_CONFIG["custom_permission_translation"]
)

APPS_CUSTOMIZATION_FUNC = import_string(
    TABLE_PERMISSIONS_CONFIG["apps_customization_func"]
)
CUSTOM_PERMISSIONS_CUSTOMIZATION_FUNC = import_string(
    TABLE_PERMISSIONS_CONFIG["custom_permissions_customization_func"]
)
