# -*- coding: UTF-8 -*-


class AuthAPI:
    def __init__(self, antsy_client, version):
        self.antsy_client = antsy_client
        self.base_path = f"auth/{version}"

    def refresh(self):
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/refresh"
        response = self.antsy_client.client.get(full_url)
        return response.json().get("data", {}).get("access_token")

    def whoami(self):
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/whoami"
        response = self.antsy_client.client.get(full_url)
        return response.json()
