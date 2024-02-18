from loguru import logger
from typing import Union

import requests
import datetime

from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from ocpy.api.api_client import OpenCastBaseApiClient

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return int((dt - epoch).total_seconds() * 1000.0)


class SigningApi(OpenCastBaseApiClient):
    def __init__(self, user=None, password=None, server_url=None, **_kwargs):
        super().__init__(user, password, server_url)
        self.base_url = self.server_url + "/signing"

    def accepts(self, url: str, **kwargs):
        u = self.base_url + "/accepts"
        logger.debug(f"url: {u}")
        res = requests.get(
            u,
            auth=HTTPBasicAuth(self.user, self.password),
            params={"baseUrl": url},
            timeout=kwargs.pop("timeout", 30),
        )
        if res.ok:
            return res.text.lower() == "true"
        logger.error(f"Error occured: {res.text} (status_code: {res.status_code})")
        return False

    def sign(self, url: str, valid_until: Union[None, int] = None, **kwargs):
        if valid_until is None:
            valid_until = unix_time_millis(datetime.datetime.now()) + 60 * 60 * 1000
        logger.debug(f"valid until: {valid_until} (unix_time_millis)")
        u = self.base_url + "/sign"
        logger.debug(f"url: {u}")
        res = requests.get(
            u,
            auth=HTTPBasicAuth(self.user, self.password),
            params={
                "baseUrl": url,
                "validUntil": valid_until,
                "validFrom": 0,
                "ipAddr": None,
            },
            timeout=kwargs.pop("timeout", 30),
        )
        if res.ok:
            return res.text
        logger.error(f"Error occured: {res.text} (status_code: {res.status_code})")
        return None
