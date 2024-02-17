import inspect
import json
import logging
import os
import random
import string
import sys
import traceback

import haggis.logs
from python_sdk_remote.mini_logger import MiniLogger
from python_sdk_remote.utilities import our_get_env, get_environment_name
from user_context_remote.user_context import UserContext

from .Component import Component
from .LoggerOutputEnum import LoggerOutputEnum
from .MessageSeverity import MessageSeverity
from .SendToLogzIo import SendTOLogzIo
from .Writer import Writer
from .debug_mode import DebugMode
from .fields import Fields

logzio_token = our_get_env("LOGZIO_TOKEN")
logzio_url = "https://listener.logz.io:8071"
COMPUTER_LANGUAGE = "Python"
loggers = {}
mandatory_fields_by_class = {}  # used by the MetaLogger


# TODO Add optional parameter to logger.start()
#  which called api_call, so logger.start will call api_management
#  to insert into api_call_table all fields including session_id.

class Logger(logging.Logger):
    @staticmethod
    def __get_base_logger(mandatory_fields, **kwargs) -> None:
        # This method is called by the metaclass to get the mandatory fields from the base classes in inheritance
        # This is needed because the metaclass is called before the __init__ method
        # Alternatively, we can return a logging.getLogger(), as those are not used in such cases,
        # but we might miss cases where the user forget to provide the mandatory fields
        mandatory_fields_to_cache = {k: v for k, v in kwargs['object'].items() if k in mandatory_fields}
        if mandatory_fields_to_cache and 'class' in kwargs.get('object', {}):
            mandatory_fields_by_class[kwargs['object']['class']] = mandatory_fields_to_cache
        if 'bases' in kwargs.get('object', {}):
            for base in kwargs['object']['bases']:
                cached_mandatory_fields = mandatory_fields_by_class.get(base.__name__, {})
                if cached_mandatory_fields:
                    kwargs['object'].update(cached_mandatory_fields)
                    break

            if not all(k in kwargs.get('object', {}) for k in mandatory_fields):
                # (I am not so sure if it is needed)
                for base in kwargs['object']['bases']:
                    if hasattr(base, 'logger'):  # if some base has logger attribute, use its mandatory fields
                        kwargs['object'].update({k: v for k, v in base.logger.additional_fields.items()})

    @staticmethod
    def create_logger(**kwargs):
        mandatory_fields = ('component_id', 'component_name', 'component_category', 'developer_email')
        Logger.__get_base_logger(mandatory_fields, **kwargs)

        if not all(k in kwargs.get('object', {}) for k in mandatory_fields):
            raise Exception(
                "please insert component_id, component_name, component_category and developer_email in your object")

        # get cached logger if exists or create a new one
        component_id = int(kwargs['object']['component_id'])
        component_category = kwargs['object']['component_category']
        unique_logger_key = (component_id, component_category)

        if unique_logger_key in loggers and not kwargs.get('ignore_cached_logger', False):
            return loggers.get(unique_logger_key)
        else:
            logger = Logger(**kwargs)
            loggers[unique_logger_key] = logger
            return logger

    def __init__(self, *,
                 handler: logging.Handler = logging.StreamHandler(stream=sys.stdout),
                 formatter: logging.Formatter = None,
                 level: int | str = None,
                 **kwargs) -> None:

        self.debug_mode = DebugMode(logger_minimum_severity=level)
        self.component_id = int(kwargs['object']['component_id'])
        self.logger_table_fields = {}
        self._writer = Writer()
        self.logzio_handler = SendTOLogzIo()
        self.write_to_sql = False
        self.user_context = None
        self.additional_fields = kwargs['object'].copy()
        self.additional_fields["session"] = self.__generate_session_id()

        self.logger = self.initiate_logger(handler=handler, formatter=formatter,
                                           level=self.debug_mode.logger_minimum_severity)
        self.logger.name = kwargs['object']['component_name']

        super().__init__(name=self.logger.name)

    @staticmethod
    def __generate_session_id(length: int = 32):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def initiate_logger(*,
                        handler: logging.Handler = logging.StreamHandler(stream=sys.stdout),
                        formatter: logging.Formatter = None,
                        level: int = None) -> logging.Logger:

        # logging levels: INFO = 20, DEBUG = 10
        haggis.logs.add_logging_level(level_name="VERBOSE", level_num=logging.DEBUG + 1, method_name="verbose")
        haggis.logs.add_logging_level(level_name="INIT", level_num=logging.DEBUG + 2, method_name="init")
        haggis.logs.add_logging_level(level_name="START", level_num=logging.DEBUG + 3, method_name="start")
        haggis.logs.add_logging_level(level_name="END", level_num=logging.DEBUG + 4, method_name="end")

        if not formatter:
            if isinstance(handler, logging.StreamHandler) and stream_supports_colour(handler.stream):
                formatter = _ColourFormatter()
            else:
                dt_fmt = '%H:%M:%S'  # '%Y-%m-%d %H:%M:%S'
                formatter = logging.Formatter('[{asctime}] [{levelname:<8}]: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger = logging.getLogger()

        our_levels_to_logging = {
            MessageSeverity.Debug: logging.DEBUG,
            MessageSeverity.Verbose: logging.VERBOSE,  # noqa
            MessageSeverity.Init: logging.INIT,  # noqa
            MessageSeverity.Start: logging.START,  # noqa
            MessageSeverity.End: logging.END,  # noqa
            MessageSeverity.Information: logging.INFO,
            MessageSeverity.Warning: logging.WARNING,
            MessageSeverity.Error: logging.ERROR,
            MessageSeverity.Exception: logging.ERROR,
            MessageSeverity.Critical: logging.CRITICAL,
        }
        # Debug = 100, Verbose = 200. If level = 101 we want the one that is bigger than 101, i.e. Verbose
        level = min(our_levels_to_logging.keys(),
                    key=lambda x: x.value if x.value >= level else MessageSeverity.Debug.value)

        logger.setLevel(our_levels_to_logging[MessageSeverity(level)])
        logger.addHandler(handler)
        return logger

    def __log(self, *, function, message_severity: MessageSeverity, log_message, **kwargs):
        if self.debug_mode.is_logger_output(component_id=self.component_id, logger_output=LoggerOutputEnum.Console,
                                            severity_level=message_severity.value):
            # TODO: should we use self.isEnabledFor(level)?
            #  https://docs.python.org/3/library/logging.html#logging.Logger.getEffectiveLevel
            if log_message or kwargs:  # filter empty logger.start() and logger.end()
                kwargs_to_print = kwargs.get('object', kwargs)
                function(f'{log_message or ""}'
                         f'{" | " if log_message and kwargs else ""}'
                         f'{("kwargs=" + str(kwargs_to_print) if kwargs else "")}')

        log_object = {
            'severity_id': message_severity.value,
            'severity_name': message_severity.name
        }
        if log_message:
            log_object['log_message'] = log_message

        if isinstance(kwargs.get('object'), Exception):
            kwargs['object'] = {"exception": kwargs['object']}

        if isinstance(kwargs.get('object', {}).get('exception'), Exception):
            exception = kwargs['object']['exception']
            stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)
            del kwargs['object']['exception']
            kwargs['object']['error_stack'] = str(stack_trace)

        if 'object' not in kwargs:
            kwargs['object'] = {}
        kwargs['object'].update(log_object)

        kwargs = self.insert_to_payload_extra_vars(**kwargs)
        self.insert_to_object(**kwargs)

        if self.write_to_sql and self.debug_mode.is_logger_output(component_id=self.component_id,
                                                                  logger_output=LoggerOutputEnum.MySQLDatabase,
                                                                  severity_level=message_severity.value):
            self._writer.add_message_and_payload(log_message, **kwargs)
        if self.debug_mode.is_logger_output(component_id=self.component_id, logger_output=LoggerOutputEnum.Logzio,
                                            severity_level=message_severity.value):
            self.logzio_handler.send_to_logzio(kwargs['object'])

    def init(self, log_message=None, **kwargs):
        # TODO: Why do we need it?
        self.__log(function=logging.init,  # noqa
                   message_severity=MessageSeverity.Init, log_message=log_message, **kwargs)

    def start(self, log_message=None, **kwargs):
        self.__log(function=logging.start,  # noqa
                   message_severity=MessageSeverity.Start, log_message=log_message, **kwargs)

    def end(self, log_message=None, **kwargs):
        self.__log(function=logging.end,  # noqa
                   message_severity=MessageSeverity.End, log_message=log_message, **kwargs)

    def info(self, log_message=None, **kwargs):
        self.__log(function=logging.info, message_severity=MessageSeverity.Information,
                   log_message=log_message, **kwargs)

    def error(self, log_message=None, **kwargs):
        self.__log(function=logging.error, message_severity=MessageSeverity.Error, log_message=log_message, **kwargs)

    def warn(self, log_message=None, **kwargs):
        # deprecated
        self.__log(function=logging.warn, message_severity=MessageSeverity.Warning, log_message=log_message,
                   **kwargs)

    def warning(self, log_message=None, **kwargs):
        self.__log(function=logging.warning, message_severity=MessageSeverity.Warning, log_message=log_message,
                   **kwargs)

    def debug(self, log_message=None, **kwargs):
        self.__log(function=logging.debug, message_severity=MessageSeverity.Debug, log_message=log_message, **kwargs)

    def critical(self, log_message=None, **kwargs):
        self.__log(function=logging.critical, message_severity=MessageSeverity.Critical, log_message=log_message,
                   **kwargs)

    def verbose(self, log_message=None, **kwargs):
        self.__log(function=logging.verbose,  # noqa
                   message_severity=MessageSeverity.Verbose, log_message=log_message, **kwargs)

    def exception(self, log_message=None, **kwargs):
        """This method should be called only in tests / top level functions / api calls.
        (not when invoking `raise` after catching an exception,
            otherwise the traceback will be wrong and logged multiple times)
        """
        self.__log(function=logging.exception, message_severity=MessageSeverity.Exception, log_message=log_message,
                   **kwargs)

    def _insert_variables(self, **kwargs):
        object_data = kwargs.get("object", {})
        self.logger_table_fields.update(object_data)
        self.additional_fields.update(object_data)

    def insert_to_object(self, **kwargs):
        object_data = kwargs.get("object", {})
        object_data.update({field: field_value for field, field_value in self.logger_table_fields.items()
                            if field_value is not None})

    def update_logger_table_fields(self) -> None:
        if self.write_to_sql:
            logger_table_fields = Fields.get_logger_table_fields()
            for field in logger_table_fields:
                self.logger_table_fields[field] = None

    def clean_variables(self):
        for field in self.logger_table_fields:
            self.logger_table_fields[field] = None
        self.additional_fields.clear()

    def insert_to_payload_extra_vars(self, **kwargs):
        try:
            self.user_context = UserContext.login_using_user_identification_and_password()
        except Exception as exception:
            MiniLogger.exception("Error while trying to login using user identification and password", exception)
        if self.user_context is not None:
            # TODO Shall we change in the database column to real_user_id?
            kwargs['object']['user_id'] = self.user_context.get_real_user_id()
            kwargs['object']['created_user_id'] = self.user_context.get_real_user_id()
            # TODO Shall we change the database to store real_profile_id and effective_profile?
            kwargs['object']['profile_id'] = self.user_context.get_real_profile_id()
            # TODO: change to display_as like we have in contact ...
            if self.user_context.real_display_name is not None:
                # TODO Shall we change current_runner to real_name?
                kwargs['object']['current_runner'] = self.user_context.get_real_name()
            else:
                kwargs['object']['current_runner'] = our_get_env("PRODUCT_USER_IDENTIFIER")
        message = kwargs['object'].pop('message', None)
        kwargs['object']['function_name'] = self.get_current_function_name()
        kwargs['object']['environment'] = get_environment_name()
        kwargs['object']['class'] = self.get_calling_class()
        kwargs['object']['line_number'] = self.get_calling_line_number()
        kwargs['object']['computer_language'] = COMPUTER_LANGUAGE
        kwargs['object'].update({field: field_value for field, field_value in self.logger_table_fields.items()
                                 if field_value is not None})
        kwargs['object'].update(self.additional_fields)
        if self.write_to_sql:
            component_json = self.get_component_json(self.component_id)
            if component_json:
                for field in component_json.keys():
                    if field not in kwargs['object']:
                        field_value = component_json[field]
                        if field_value is not None:
                            kwargs['object'][field] = field_value
        if message is not None:
            kwargs['object']['message'] = message
        object_data = kwargs.get("object", {})
        object_data["record"] = json.dumps({key: str(value) for key, value in object_data.items()})
        if self.write_to_sql:
            object_data = {key: value for key, value in object_data.items() if key in self.logger_table_fields.keys()}
            kwargs["object"] = object_data
        return kwargs

    @staticmethod
    def get_current_function_name():
        stack = inspect.stack()
        # 0 = 'get_current_function_name', 1 = 'insert_to_payload_extra_vars', 2 = '__log', 3 = start/end/info...
        caller_frame = stack[4]
        function_name = caller_frame.function
        return function_name

    @staticmethod
    def get_calling_class():
        stack = inspect.stack()
        calling_module = inspect.getmodule(stack[4].frame)
        return calling_module.__name__

    @staticmethod
    def get_calling_line_number():
        stack = inspect.stack()
        calling_frame = stack[4]
        line_number = calling_frame.lineno
        return line_number

    def get_component_json(self, component_id: int) -> dict:
        component_json = Component.get_details_by_component_id(component_id)
        self.logger_table_fields.update(component_json)
        return component_json

    def is_component_complete(self):
        return (getattr(self, 'component_name') is None
                or getattr(self, 'component_type') is None
                or getattr(self, 'component_category') is None
                or getattr(self, 'testing_framework') is None
                or getattr(self, 'api_type') is None
                )

    def set_write_to_sql(self, value: bool) -> None:  # TODO: not called
        self.write_to_sql = value
        if self.write_to_sql:
            self.update_logger_table_fields()


# Copyright: https://github.com/Rapptz/discord.py/blob/master/discord/utils.py#L1241
def is_docker() -> bool:
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))


def stream_supports_colour(stream) -> bool:
    # Pycharm and Vscode support colour in their inbuilt editors
    COLORS_IN_LOGS = our_get_env("COLORS_IN_LOGS", "")
    if COLORS_IN_LOGS.lower() == "true":
        return True
    elif COLORS_IN_LOGS.lower() == "false":
        return False

    if 'PYCHARM_HOSTED' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode':
        return True

    is_a_tty = hasattr(stream, 'isatty') and stream.isatty()  # TTY = terminal
    if sys.platform != 'win32':
        # Docker does not consistently have a tty attached to it
        return is_a_tty or is_docker()

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    return is_a_tty or ('ANSICON' in os.environ or 'WT_SESSION' in os.environ)


class _ColourFormatter(logging.Formatter):
    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # '1' means bold, '2' means dim, '0' means reset, and '4' means underline.

    def format(self, record):
        level_colours = [
            (logging.DEBUG, '\x1b[40;1m'),  # Debug level in bold black background
            (logging.VERBOSE, '\x1b[36;1m'),  # Verbose level in bold cyan foreground   # noqa
            (logging.INIT, '\x1b[46;1m'),  # Init level in bold cyan background         # noqa
            (logging.START, '\x1b[42;1m'),  # Start level in bold green background      # noqa
            (logging.END, '\x1b[41;1m'),  # End level in bold red background            # noqa
            (logging.INFO, '\x1b[34;1m'),  # Info level in bold blue foreground
            (logging.WARNING, '\x1b[33;1m'),  # Warning level in bold yellow foreground
            (logging.ERROR, '\x1b[31m'),  # Error level in red foreground
            (logging.CRITICAL, '\x1b[41m'),  # Critical level with red background
        ]

        formats = {
            level: logging.Formatter(
                f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[0m %(message)s',
                '%H:%M:%S',  # '%Y-%m-%d %H:%M:%S'
            )
            for level, colour in level_colours
        }

        formatter = formats.get(record.levelno, formats[logging.DEBUG])

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output
