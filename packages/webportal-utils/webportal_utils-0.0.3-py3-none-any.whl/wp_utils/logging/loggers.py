import logging
from copy import deepcopy
from logging import LogRecord

from wp_utils.settings import settings


class CropLogger(logging.Logger):
    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ) -> LogRecord:
        if args and settings.CROP_LOG:
            args = list(args)
            args = self.crop_args(args)
        return super().makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

    def crop_args(self, args) -> list:
        args = list(args)
        for index, arg in enumerate(args):
            if isinstance(arg, str):
                args[index] = arg[: settings.MAX_LOG_ARG_LENGTH]
            elif isinstance(arg, dict):
                args[index] = self.crop_dict(arg)
        return tuple(args)

    def crop_dict(self, message) -> dict:
        updated_message = deepcopy(message)
        for key, value in message.items():
            if isinstance(value, dict):
                value = self.crop_dict(value)
            elif isinstance(value, str):
                value = value[: settings.MAX_LOG_ARG_LENGTH]
            updated_message[key] = value
        return updated_message
