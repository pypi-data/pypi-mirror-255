# -*- coding: UTF-8 -*-


class AntsyError(Exception):
    fmt = "An unspecified error occurred"

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class CustomerNotFound(AntsyError):
    fmt = "Customer not found: '{customer_uid}'"


class InvalidCountryCode(AntsyError):
    fmt = "Invalid country code: '{country_code}'"
