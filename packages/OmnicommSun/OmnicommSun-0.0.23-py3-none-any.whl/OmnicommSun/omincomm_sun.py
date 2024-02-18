import json
import requests as r


class SUN:
    URL = "https://config.omnicomm.ru/api"

    def __init__(self):
        self._start()

    def _start(self):
        params = f'{self.URL}?action=locale&lang=ru'
        r.post(params)

    def _get_task_queue(self):
        data = {
            "action": "getTaskQueue"
        }
        response = r.post(url=self.URL, data=data)
        return response

    def get_registrator_settings(self, terminal_id: int, password: str):
        """
        :param terminal_id: номер терминала
        :param password: пароль
        :return: настройки терминала
        """
        data = {
            "action": "getRegistrator",
            "data": json.dumps({
                "ID": terminal_id,
                "password": password,
                "registratorid": []
            })
        }
        response = r.post(url=self.URL, params=data)
        return response.json()

