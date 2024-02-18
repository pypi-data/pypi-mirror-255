# -*- coding: UTF-8 -*-

import logging

import httpx

from .namespaces.appointments import AppointmentsAPI
from .namespaces.auth import AuthAPI


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Antsy:
    def __init__(self, refresh_token: str, version="v1") -> None:
        self.base_url = "https://api.antsy.app"
        self.version = version
        self.access_token = self._fetch_access_token(refresh_token)
        self.client = httpx.Client(http2=True, headers={"Authorization": f"Bearer {self.access_token}"})

        self._appointments = AppointmentsAPI(self, version)
        self._auth = AuthAPI(self, version)

    def _fetch_access_token(self, refresh_token: str) -> str:
        try:
            with httpx.Client(http2=True, headers={"Authorization": f"Bearer {refresh_token}"}) as temp_client:
                response = temp_client.get(f"{self.base_url}/auth/{self.version}/refresh")
                response.raise_for_status()
                return response.json().get("data", {}).get("access_token")
        except Exception as exc:
            logger.error(f"Error getting access token: {exc}")
            raise

    def close(self) -> None:
        """Close the httpx client."""
        self.client.close()

    @property
    def appointments(self):
        return self._appointments

    @property
    def auth(self):
        return self._auth
