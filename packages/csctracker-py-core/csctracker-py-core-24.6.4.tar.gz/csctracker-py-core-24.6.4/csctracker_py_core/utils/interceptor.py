import logging
import threading
import time
from datetime import datetime

from csctracker_queue_scheduler.services.scheduler_service import SchedulerService
from flask import Flask, request, g

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.repository.http_repository import HttpRepository
from csctracker_py_core.utils.configs import Configs
from csctracker_py_core.utils.request_info import RequestInfo
from csctracker_py_core.utils.utils import Utils
from csctracker_py_core.utils.version import Version


class Interceptor:
    def __init__(self, app: Flask, http_repository: HttpRepository, save_request=False):
        self.logger = logging.getLogger()
        self.app = app
        self.http_repository = http_repository
        self.save_request = save_request
        self.__init()

    def __init(self):
        @self.app.before_request
        def start_timer():
            g.start = time.time()
            correlation_id = RequestInfo.get_correlation_id()
            g.correlation_id = correlation_id
            thread = threading.current_thread()
            thread.correlation_id = correlation_id

        @self.app.after_request
        def log_request(response):
            now = time.time()
            duration = round(now - g.start, 2)
            log_entry = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'args': dict(request.args),
                'duration': f'{duration}s',
                'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)),
                'requestId': g.correlation_id,
                'appName': Version.get_app_name(),
                'appVersion': Version.get_version(),
            }
            if Configs.get_env_variable(Config.LOG_RESPONSE_BODY) == 'True':
                log_entry['response'] = response.get_json()

            if Configs.get_env_variable(Config.LOG_REQUEST_BODY) == 'True':
                try:
                    log_entry['request'] = request.get_json()
                except Exception:
                    pass
            if request.path in ['/metrics', '/health']:
                self.logger.debug(log_entry)
            else:
                self.logger.info(log_entry)
            if self.save_request:
                self.save_request_info(request, response, request.path)
            return response

    def save_request_info(self, request_, response, path):
        try:
            data = response.get_data()
            decoded_data = data.decode('utf-8', 'ignore')
            headers_ = Utils.conv_keys_to_lower(dict(request_.headers))
            if 'x-correlation-id' not in headers_:
                headers_['x-correlation-id'] = RequestInfo.get_request_id()
            request_info_ = {
                "path": path,
                "method": request_.method,
                "headers": str(headers_),
                "parameters": str(dict(request_.args)),
                "body": request_.get_data(as_text=True),
                "response": decoded_data,
                "success": 'S' if response.status_code < 400 else 'F',
                "duration": round(time.time() - g.start, 2),
                "request_id": RequestInfo.get_request_id(),
                "date_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Configs.get_env_variable(Config.API_TOKEN)}",
                "x-correlation-id": RequestInfo.get_request_id()
            }
            args_ = {
                'url': f"{Configs.get_env_variable(Config.URL_BFF)}rabbit/requests",
                'body': request_info_,
                'headers': headers
            }
            SchedulerService.put_in_queue(self.http_repository.post, args=args_, priority=True)
        except Exception as e:
            logging.getLogger().error(f"Error: {str(e)}")
            pass
