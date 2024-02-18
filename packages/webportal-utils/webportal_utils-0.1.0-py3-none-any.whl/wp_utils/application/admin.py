import importlib

from django.contrib import admin, messages
from django.core.cache import cache
from django.utils.safestring import SafeString, mark_safe

from wp_utils.settings import utils_settings

DEFAULT_VERSION = "n/a"


class RecordEditorLock(admin.ModelAdmin):
    table = ""
    session = ""
    timeout = utils_settings.BLOCK_RECORD_TIMEOUT

    def __set_variables(self, path: str, session: str) -> None:
        self.table = utils_settings.SERVICE_NAME + "_" + path
        self.session = session

    def __set_cache(self) -> None:
        cache.set(
            self.table,
            self.session,
            timeout=self.timeout,
        )

    def __password_on_change(self, http_referer: str) -> bool:
        if "password" not in http_referer:
            return False
        check_path = ("/admin/" + http_referer.split("/admin/")[1]).split("password/")[0] + "change/"
        if self.table != utils_settings.SERVICE_NAME + "_" + check_path:
            return False
        self.__set_cache()
        return True

    def __check_cache_record(self) -> bool:
        if not cache.get(self.table):
            self.__set_cache()
        return self.session == cache.get(self.table)

    def has_change_permission(self, request, obj=None):
        if "change" in request.path:
            self.__set_variables(request.path, request.session.session_key)
            if self.__password_on_change(request.META.get("HTTP_REFERER", "")):
                return True
            if not self.__check_cache_record():
                return False
        self.__set_cache()
        return super().has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        if "change" in request.path:
            self.__set_variables(request.path, request.session.session_key)
            if self.__password_on_change(request.META.get("HTTP_REFERER", "")):
                return True
            if not self.__check_cache_record():
                return False
        self.__set_cache()
        return super().has_delete_permission(request, obj)

    def has_view_or_change_permission(self, request, obj=None):
        if "change" in request.path:
            self.__set_variables(request.path, request.session.session_key)
            if self.__password_on_change(request.META.get("HTTP_REFERER", "")):
                return self.has_view_permission(request, obj) or self.has_change_permission(request, obj)
            if not self.__check_cache_record():
                messages.error(request, "Запись уже редактируется другим пользователем")

        return self.has_view_permission(request, obj) or self.has_change_permission(request, obj)


def make_site_header(project_module: str) -> SafeString:
    try:
        module = importlib.import_module(project_module)
        version = module.__version__
    except (ImportError, AttributeError):
        version = DEFAULT_VERSION
    header = f"Панель администратора: <br> микросервис '{utils_settings.SERVICE_NAME}' (v.{version})"
    return mark_safe(header)


def make_site_title() -> str:
    return f"Микросервис '{utils_settings.SERVICE_NAME.capitalize()}'"
