# -*- coding: UTF-8 -*-
import logging
from typing import List, Optional

from httpx import HTTPStatusError

from antsy.exceptions import AntsyError, CustomerNotFound
from .models import Customer


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CustomersAPI:
    def __init__(self, antsy_client, version):
        self.antsy_client = antsy_client
        self.base_path = f"customers/{version}"

    def get(self, customer_uid: str) -> Optional[Customer]:
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/customer/{customer_uid}"

        try:
            response = self.antsy_client.client.get(full_url).json()
        except HTTPStatusError as exc:
            logger.error(f"Error: {exc}")
            return None

        if response.get("status") != "ok":
            if response.get("message") == "CUSTOMER_NOT_FOUND":
                raise CustomerNotFound(customer_uid=customer_uid)
            if response.get("message") == "DATABASE_ERROR":
                raise AntsyError()

            return None

        data = response.get("data")
        return Customer.model_validate(data.get("customer"))

    def create(self):
        pass

    def search(self):
        pass
