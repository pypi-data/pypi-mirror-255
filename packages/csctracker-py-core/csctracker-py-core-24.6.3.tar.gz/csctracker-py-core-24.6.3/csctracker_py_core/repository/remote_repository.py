import logging

import requests

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.utils.configs import Configs


class RemoteRepository:
    def __init__(self):
        self.logger = logging.getLogger()
        self.url_repository = Configs.get_env_variable(Config.URL_REPOSITORY, default='http://bff:8080/repository/')
        if self.url_repository[-1] != '/':
            self.url_repository += '/'
        pass

    def insert(self, table, data, headers=None):
        try:
            response = requests.post(self.url_repository + table, headers=headers, json=data)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error inserting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def update(self, table, keys=None, data=None, headers=None):
        params = self.get_params(data, keys)
        try:
            response = requests.post(self.url_repository + table, headers=headers, json=data, params=params)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error updating data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def delete_all(self, table, headers=None):
        self.delete(table, [], {}, headers=headers)

    def delete(self, table, keys=None, data=None, headers=None):
        params = self.get_params(data, keys)
        try:
            response = requests.post(self.url_repository + "delete/" + table, headers=headers, json=data, params=params)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error deleting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def add_user_id(self, data, headers=None):
        user = self.get_user(headers)
        data['user_id'] = user['id']
        return data

    def get_user(self, headers=None):
        user_name = headers.get('userName')
        try:
            user = self.get_object('users', data={'email': user_name}, headers=headers)
            return user
        except Exception as e:
            raise e

    def get_object(self, table, keys=None, data=None, headers=None):
        params = self.get_params(data, keys)
        try:
            response = requests.get(self.url_repository + 'single/' + table, params=params, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def get_all_objects(self, table, headers=None):
        return self.get_objects(table, [], {}, headers)

    def get_objects(self, table, keys=None, data=None, headers=None):
        params = self.get_params(data, keys)
        try:
            response = requests.get(self.url_repository + table, params=params, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def execute_select(self, select, headers=None):
        command = {
            'command': select
        }
        try:
            response = requests.post(self.url_repository + "command/select", headers=headers, json=command)
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f'Error getting data: {response.text}')
            return response.json()
        except Exception as e:
            raise e

    def exist_by_key(self, table, key=[], data={}, headers=None):
        try:
            objects = self.get_objects(table, key, data, headers)
            return objects.__len__() > 0
        except Exception as e:
            self.logger.exception(e)
            return False

    def get_params(self, data, keys):
        if data is None:
            data = {}
        params = {}
        if keys is None:
            keys = []
        if keys.__len__() > 0:
            for key in keys:
                params[key] = data[key]
            return params
        for key in data.keys():
            params[key] = data[key]
        return params
