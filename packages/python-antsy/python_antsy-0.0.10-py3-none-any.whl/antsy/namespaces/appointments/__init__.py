# -*- coding: UTF-8 -*-


class AppointmentsAPI:
    def __init__(self, antsy_client, version):
        self.antsy_client = antsy_client
        self.base_path = f"appointments/{version}"

    def get_appointments(self, queue_uid: str):
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/queue/{queue_uid}"

        response = self.antsy_client.client.get(full_url)
        return response.json()
