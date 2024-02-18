import logging
from typing import Any, Dict

import pysolr
from pythonjsonlogger.jsonlogger import JsonFormatter

from wp_utils.settings import utils_settings


class SolrFormatter(JsonFormatter):
    def format(self, record: logging.LogRecord) -> dict:
        """Formats a log record and serializes to json"""
        message_dict: Dict[str, Any] = {}
        # FIXME: logging.LogRecord.msg and logging.LogRecord.message in typeshed
        #        are always type of str. We shouldn't need to override that.
        if isinstance(record.msg, dict):
            message_dict = record.msg
            record.message = ""
        else:
            record.message = record.getMessage()
        # only format time if needed
        if "asctime" in self._required_fields:
            record.asctime = self.formatTime(record, self.datefmt)

        # Display formatted exception, but allow overriding it in the
        # user-supplied dict.
        if record.exc_info and not message_dict.get("exc_info"):
            message_dict["exc_info"] = self.formatException(record.exc_info)
        if not message_dict.get("exc_info") and record.exc_text:
            message_dict["exc_info"] = record.exc_text
        # Display formatted record of stack frames
        # default format is a string returned from :func:`traceback.print_stack`
        if record.stack_info and not message_dict.get("stack_info"):
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        log_record: Dict[str, Any] = dict()
        self.add_fields(log_record, record, message_dict)

        return log_record


class SolrHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.solr = pysolr.Solr(utils_settings.SOLR_LOGS_URL, always_commit=True)
        self.solr.ping()

    def emit(self, record: logging.LogRecord) -> None:
        json_record = self.format(record)
        try:
            self.solr.add([json_record])
        except pysolr.SolrError:
            json_record["message"] = json_record["message"][0 : utils_settings.SOLR_LOGS_MAX_LENGTH]
            self.solr.add([json_record])
