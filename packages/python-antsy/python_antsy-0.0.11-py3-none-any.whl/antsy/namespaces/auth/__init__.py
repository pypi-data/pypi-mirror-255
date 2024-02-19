# -*- coding: UTF-8 -*-
import logging
from typing import Optional

from httpx import HTTPStatusError

from .models import AccessToken, WhoAmI

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AuthAPI:
    def __init__(self, antsy_client, version):
        self.antsy_client = antsy_client
        self.base_path = f"auth/{version}"

    def refresh(self) -> Optional[AccessToken]:
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/refresh"

        try:
            response = self.antsy_client.client.get(full_url).json()
        except HTTPStatusError as exc:
            logger.error(f"Error: {exc}")
            return None

        if response.get("status") != "ok":
            return None

        return AccessToken.model_validate(response.get("data"))

    def whoami(self) -> Optional[WhoAmI]:
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/whoami"
        try:
            response = self.antsy_client.client.get(full_url).json()
        except HTTPStatusError as exc:
            logger.error(f"Error: {exc}")
            return None

        if response.get("status") != "ok":
            return None

        return WhoAmI.model_validate(response.get("data"))
