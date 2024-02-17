import asyncio
import functools
import json
import logging
from typing import Callable

from starlette import status

from wp_utils.settings import settings


class LoggingMixin:
    app_logger: logging.Logger = logging.getLogger("app")

    def __getattribute__(self, item: str):
        attr = super(LoggingMixin, self).__getattribute__(item)
        if item in settings.LOGGING_MIXIN_DECORATE:
            return self.__decorate(attr, item)
        return attr

    def __decorate(self, func: Callable, func_name: str):
        @functools.wraps(func)
        def decorator(data):
            self.app_logger.info(
                "%s.%s() payload=%s",
                self.__class__.__name__,
                func_name,
                data.get("body"),
                extra=self.__build_extra(data=data),
            )

            try:
                response = dict(func(data))
            except Exception as ex:
                self.app_logger.error(
                    "%s.%s() error=%s",
                    self.__class__.__name__,
                    func_name,
                    str(ex),
                    extra=self.__build_extra(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR),
                )

                raise
            self.app_logger.info(
                "%s.%s() message=%s",
                self.__class__.__name__,
                func_name,
                response.get("status", {}).get("message"),
                extra=self.__build_extra(data=data, response=response),
            )

            return response

        @functools.wraps(func)
        async def async_decorator(data):
            self.app_logger.info(
                "%s.%s() payload=%s",
                self.__class__.__name__,
                func_name,
                data.get("body"),
                extra=self.__build_extra(data=data),
            )
            try:
                response = dict(await func(data))
            except Exception as ex:
                self.app_logger.error(
                    "%s.%s() error=%s",
                    self.__class__.__name__,
                    func_name,
                    str(ex),
                    extra=self.__build_extra(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR),
                )
                raise

            self.app_logger.info(
                "%s.%s() message=%s",
                self.__class__.__name__,
                func_name,
                response.get("status", {}).get("message"),
                extra=self.__build_extra(data=data, response=response),
            )
            return response

        if asyncio.iscoroutinefunction(func):
            return async_decorator
        else:
            return decorator

    def __build_extra(self, data: dict = None, response: dict = None, **kwargs):
        extra = {
            "service_name": settings.SERVICE_NAME,
        }
        if data:
            extra.update(
                {
                    "request_body": json.dumps(dict(data.get("body")), default=str),
                    "request_id": str(data.get("request_id")),
                    "request_type": data.get("request_type"),
                }
            )
        if response:
            extra.update({"status": response.get("status", {}).get("code")})
        extra.update(kwargs)
        return extra
