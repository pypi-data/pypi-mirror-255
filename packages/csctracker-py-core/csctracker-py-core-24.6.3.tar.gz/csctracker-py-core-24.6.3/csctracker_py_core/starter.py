import logging
import os

from csctracker_queue_scheduler.services.scheduler_service import SchedulerService
from flask import Flask
from flask_cors import CORS
from flask_swagger_generator.generators.swagger_view import SwaggerView
from prometheus_flask_exporter import PrometheusMetrics

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.repository.http_repository import HttpRepository
from csctracker_py_core.repository.remote_repository import RemoteRepository
from csctracker_py_core.utils.configs import Configs
from csctracker_py_core.utils.interceptor import Interceptor
from csctracker_py_core.utils.version import Version


class Starter:
    def __init__(self, static_folder="static", save_request=False):
        self.logger = logging.getLogger()
        self.app = Flask(__name__, static_folder=static_folder)
        try:
            os.environ.pop("FLASK_RUN_FROM_CLI")
        except:
            pass
        try:
            os.environ.pop("FLASK_ENV")
        except:
            pass
        SchedulerService.init(10)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.config = Configs(os.getenv('PROFILE', 'dev'))
        self.remote_repository = RemoteRepository()
        self.http_repository = HttpRepository(remote_repository=self.remote_repository)
        self.interceptor = Interceptor(self.app, self.http_repository, save_request=save_request)
        self.metrics = PrometheusMetrics(
            self.app,
            group_by='endpoint',
            default_labels={
                'application': Version.get_app_name()
            }
        )

    def get_remote_repository(self):
        return self.remote_repository

    def get_http_repository(self):
        return self.http_repository

    def get_app(self):
        return self.app

    def start(self):
        SwaggerView.init(
            self.app,
            application_name=Version.get_app_name(),
            application_version=Version.get_version(),
            swagger_destination_path='swagger.yaml'
        )
        self.app.run(host='0.0.0.0',
                     port=Configs.get_env_variable(Config.PORT, default=5000))
