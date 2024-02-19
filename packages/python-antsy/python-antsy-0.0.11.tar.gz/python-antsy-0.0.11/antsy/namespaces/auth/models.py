# -*- coding: UTF-8 -*-

import pydantic


class AccessToken(pydantic.BaseModel):
    access_token: str


class WhoAmI(pydantic.BaseModel):
    identity: str
