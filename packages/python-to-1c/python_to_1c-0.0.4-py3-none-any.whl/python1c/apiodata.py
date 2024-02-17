import json
import requests

from .core import ServerConnection


class APIOdata:
    """Запросы к БД 1С"""
    server_info: ServerConnection

    def __init__(self, server_info: ServerConnection) -> None:
        self.server_info = server_info
        self.url = self.server_info.full_url + '?'

    def get(self, guid, select=None) -> str:
        """Получение конкреного объекта"""
        obj = f"(guid'{guid}')"
        url = f'{self.server_info.full_url}{obj}'
        if select:
            url += f'?&$select={select}'
        response = requests.get(url, auth=self.server_info.auth,
                                headers=self.server_info.headers)
        if response.status_code != 200:
            raise Exception(response.text)
        return json.loads(response.text)

    def list(self, **kwargs) -> str:
        """Получение списка объектов"""
        url = self.url
        filter_list = ['top', 'skip', 'select', 'filter', 'expand', 'orderby']
        for key, value in kwargs.items():
            if key in filter_list:
                url += f'&${key}={value}'
        response = requests.get(url, auth=self.server_info.auth,
                                headers=self.server_info.headers)
        if response.status_code != 200:
            raise Exception(response.text)
        return json.loads(response.text)['value']

    def create(self, data) -> str:
        """Создание объекта"""
        response = requests.post(self.url, auth=self.server_info.auth,
                                 headers=self.server_info.headers, data=json.dumps(data))
        if response.status_code != 201:
            raise Exception(response.text)
        return json.loads(response.text)

    def edit(self, guid, data) -> str:
        """Редактирование объекта"""
        url = self.server_info.full_url + f"(guid'{guid}'" + '?'
        response = requests.patch(url, auth=self.server_info.auth,
                                  headers=self.server_info.headers, data=json.dumps(data))
        if response.status_code != 200:
            raise Exception(response.text)
        return json.loads(response.text)
