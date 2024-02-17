from logging import LogRecord

from logzio.handler import LogzioHandler
from python_sdk_remote.mini_logger import MiniLogger
from python_sdk_remote.utilities import our_get_env

LOGZIO_URL = "https://listener.logz.io:8071"
LOGZIO_TOKEN = our_get_env("LOGZIO_TOKEN")

logzio_handler = LogzioHandler(token=LOGZIO_TOKEN, url=LOGZIO_URL)


class SendTOLogzIo:
    @staticmethod
    def send_to_logzio(data: dict):
        try:
            log_record = CustomLogRecord(
                name="log",
                level=data.get('severity_id'),
                pathname=LOGZIO_URL,
                lineno=data.get("line_number"),
                msg=data.get('record'),
                args=data
            )
            logzio_handler.emit(log_record)
        except Exception as exception:
            MiniLogger.exception("Failed to send log to Logz.io", exception)


class CustomLogRecord(LogRecord):
    def __init__(self,
                 name: str,
                 level: int,
                 pathname: str,
                 lineno: int,
                 msg: str,
                 args,
                 exc_info=None,
                 func: str | None = None,
                 sinfo: str | None = None) -> None:
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            try:
                msg = self.msg.format(*self.args)
            except Exception:
                pass
        return msg
