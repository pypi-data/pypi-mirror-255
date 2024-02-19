# -*- coding: UTF-8 -*-
import logging
from typing import List, Optional

from dateutil.parser import parse
from httpx import HTTPStatusError

from .models import Queue, QueueAppointment

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AppointmentsAPI:
    def __init__(self, antsy_client, version):
        self.antsy_client = antsy_client
        self.base_path = f"appointments/{version}"

    def get(self, queue_uid: str) -> Optional[List[QueueAppointment]]:
        full_url = f"{self.antsy_client.base_url}/{self.base_path}/queue/{queue_uid}"

        try:
            response = self.antsy_client.client.get(full_url).json()
        except HTTPStatusError as exc:
            logger.error(f"Error: {exc}")
            return None

        if response.get("status") != "ok":
            return None

        data = response.get("data")
        queue = Queue.model_validate(data.get("queue"))

        output: List[QueueAppointment] = []
        for appointment in data.get("appointments"):
            entry = {"uid": appointment.get("uid")}
            entry["day"] = parse(appointment.get("day")).date()
            entry["start_time"] = parse(appointment.get("start_time"))

            output.append(QueueAppointment.model_validate(entry))

        return output

    def create(self):
        pass
