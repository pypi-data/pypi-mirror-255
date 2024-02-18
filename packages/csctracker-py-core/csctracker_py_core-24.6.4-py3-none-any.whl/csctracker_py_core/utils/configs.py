import decimal
import json
import logging
import os

from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.utils.request_info import RequestInfo
from csctracker_py_core.utils.version import Version


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['requestId'] = RequestInfo.get_request_id()
        log_record['appName'] = Version.get_app_name()
        log_record['appVersion'] = Version.get_version()
        log_record['name'] = \
            f"{os.path.splitext(os.path.basename(record.pathname))[0]}.{record.funcName}:{record.lineno}"


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)


class Configs:
    def __init__(self, env):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.logger = logging.getLogger()
        self.logger.setLevel(Configs.log_level())
        formatter = CustomJsonFormatter('%(levelname)s %(name)s %(requestId)s %(appName)s %(message)s')
        json_handler = logging.StreamHandler()
        json_handler.setFormatter(formatter)
        self.logger.addHandler(json_handler)
        self.env = env
        self.load_env()

        for config in Config:
            value = self.get_env_variable(config)
            self.logger.debug(f"{config.name} = {value}")

    def load_env(self):
        env_file = f"config/{self.env}.env"
        os.environ['APPLICATION_VERSION'] = Version.get_version()
        os.environ['APPLICATION_NAME'] = Version.get_app_name()
        load_dotenv(env_file)

    @staticmethod
    def get_env_variable(key: Config, debug=False, default=None):
        try:
            getenv = os.getenv(key.name)
            if debug:
                logging.getLogger().debug(f"{key.name} = {getenv}")
            if getenv is None:
                return default
            try:
                return int(getenv)
            except Exception:
                return getenv
        except KeyError:
            return default

    @staticmethod
    def is_debug():
        variable = Configs.get_env_variable(Config.DEBUG)
        return variable == 1

    @staticmethod
    def log_level():
        variable = Configs.get_env_variable(Config.LOG_LEVEL)

        if variable is None:
            variable = 'INFO'
        variable = variable.upper()
        if variable == 'DEBUG':
            return logging.DEBUG
        elif variable == 'INFO':
            return logging.INFO
        elif variable == 'WARNING':
            return logging.WARNING
        elif variable == 'ERROR':
            return logging.ERROR
        elif variable == 'CRITICAL':
            return logging.CRITICAL
        else:
            return logging.INFO
