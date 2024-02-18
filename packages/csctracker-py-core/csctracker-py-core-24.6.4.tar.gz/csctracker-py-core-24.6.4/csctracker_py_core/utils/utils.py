import calendar
import datetime
import decimal
import json
import logging
import os
from datetime import datetime
from urllib.parse import quote

import pytz
import requests

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.utils.configs import Configs
from csctracker_py_core.utils.version import Version


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def work_time():
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        h = h - 3
        return 8 <= h <= 19

    @staticmethod
    def work_day():
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        return wd < 5

    @staticmethod
    def read_file(file_name):
        file_dir = os.path.dirname(os.path.realpath('__file__'))
        file_name = os.path.join(file_dir, file_name)
        file_handle = open(file_name)
        content = file_handle.read()
        file_handle.close()
        return content

    @staticmethod
    def get_diff_time(time_a, time_b):
        try:
            time_a = datetime.strptime(time_a, "%Y-%m-%d %H:%M:%S")
        except:
            time_a = datetime.strptime(time_a, "%Y-%m-%d %H:%M:%S.%f")

        try:
            time_b = datetime.strptime(time_b, "%Y-%m-%d %H:%M:%S")
        except:
            time_b = datetime.strptime(time_b, "%Y-%m-%d %H:%M:%S.%f")
        diff = time_b - time_a
        return diff.seconds

    @staticmethod
    def get_format_date_time(dt_string, format):
        try:
            dt_string = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        except:
            dt_string = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%f")
        return dt_string.strftime(format)

    @staticmethod
    def get_format_date_time_in_tz(dt_string, format, original_tz='America/Sao_Paulo', new_tz='UTC'):
        dt_obj = datetime.strptime(dt_string, format)

        original_tz_ = pytz.timezone(original_tz)
        dt_obj = original_tz_.localize(dt_obj)

        new_tz_ = pytz.timezone(new_tz)
        new_dt_obj = dt_obj.astimezone(new_tz_)

        return new_dt_obj.strftime(format)

    @staticmethod
    def inform_to_client(json_, operation, headers, msg=None, from_=None):

        try:
            json_ = json.dumps(json_, cls=Encoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            pass

        message = {
            "text": msg,
            "data": json_,
            "app": Version.get_app_name(),
            "operation": operation
        }

        if from_ is not None:
            message['from'] = from_

        response = requests.post(
            f"{Configs.get_env_variable(Config.URL_BFF, default='http://bff:8080/')}notify-sync/message",
            headers=headers, json=message)
        if response.status_code != 200:
            logging.getLogger().info(response.status_code)
        pass

    @staticmethod
    def all_days(month, year):

        num_days = calendar.monthrange(int(year), int(month))[1]

        all_days = [day for day in range(1, num_days + 1)]

        return all_days

    @staticmethod
    def last_month_day(month, year):
        return str(calendar.monthrange(int(year), int(month))[1])

    @staticmethod
    def fill_left(value, size, fill_char='0'):
        return str(value).rjust(size, fill_char)

    @staticmethod
    def to_url_encode(value):
        if value is None:
            return None
        return quote(value)

    @staticmethod
    def conv_keys_to_lower(d):
        return {k.lower(): v for k, v in d.items()}
