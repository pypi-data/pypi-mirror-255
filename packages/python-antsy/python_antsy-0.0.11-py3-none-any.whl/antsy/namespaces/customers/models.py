# -*- coding: UTF-8 -*-

import pydantic


class Customer(pydantic.BaseModel):
    id: str
    uid: str
    first_name: str
    last_name: str
    name: str = None
    middle_name: str = None
