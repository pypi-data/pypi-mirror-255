import requests


class ServerConnection:
    """Класс отвечающий за подключение к базе 1С"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }

    def __init__(self,
                 server_info: str,
                 info_base: str,
                 base_name: str,
                 catalog_name: str,
                 username: str,
                 password: str) -> None:
        self.server_info: str = server_info
        self.infobase: str = info_base
        self.base_name: str = base_name
        self.catalog_name: str = catalog_name
        self.full_url: str = server_info + info_base + \
                        f'/odata/standard.odata/{base_name}_{catalog_name}'
        self.auth: str = requests.auth.HTTPBasicAuth(username, password)
