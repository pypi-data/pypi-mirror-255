import json
import logging

import requests

logger = logging.getLogger("Request")

API_VERSION = "v1"


def _check_for_error(r):
    if not r.ok:
        logger.error(json.dumps(json.loads(r.text), indent=4))
    r.raise_for_status()


class _Request:
    def __init__(self, token, host):
        self.token = token
        self.host = host

    def _get_route(self):
        return f"{self.host}/{API_VERSION}"

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _make_request(
        self,
        method,
        url,
        params=None,
        files=None,
        list=False,
        throw_error=True,
        print_error=True,
    ):
        if method == "POST":
            r = requests.post(
                f"{self._get_route()}{url}",
                headers=self._get_headers(),
                json=params,
                files=files,
                verify=False,
            )
        elif method == "GET":
            r = requests.get(
                f"{self._get_route()}{url}", headers=self._get_headers(), params=params, verify=False
            )
        elif method == "DELETE":
            r = requests.delete(
                f"{self._get_route()}{url}", headers=self._get_headers(), json=params, verify=False
            )
        elif method == "PATCH":
            r = requests.patch(
                f"{self._get_route()}{url}",
                headers=self._get_headers(),
                json=params,
                verify=False
            )
        else:
            raise Exception("Method must be GET, POST, PATCH or DELETE")

        if print_error:
            if not r.ok:
                logger.error(json.dumps(json.loads(r.text), indent=4))
        if throw_error:
            r.raise_for_status()

        if r.content:
            if list:
                return r.json()["data"]
            else:
                return r.json()
