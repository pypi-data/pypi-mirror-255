# -*- coding: UTF-8 -*-

import datetime

import pydantic


class Queue(pydantic.BaseModel):
    uid: str
    name: str


class QueueAppointment(pydantic.BaseModel):
    uid: str
    day: datetime.date
    start_time: datetime.datetime
