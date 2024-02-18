"""Trusted Twin API call library"""
import logging
import json
import requests
import urllib

from typing import Any, Dict, Tuple, Optional, cast
from time import sleep
from base64 import b64encode

from trustedtwin.tt_api_base import TTEndpointBase, TTRESTServiceBase, _TT_RETRIES, _TT_RETRIES_SLEEP, _TT_DICT_HEADER, _LOG_TEMPLATE

logger = logging.getLogger(__name__)


class TTSyncEndpoint(TTEndpointBase):
    """Trusted Twin synchronous endpoint (uses standard request or session)."""

    def __init__(self, method: str, url: str, headers: Dict, session: Optional[requests.Session] = None, codes: Optional[Dict] = None) -> None:
        super().__init__(method, url, headers, session, codes)

        if not isinstance(session, requests.Session):
            self._http_routine = requests.request
        else:
            self._http_routine = cast(requests.Session, self.session).request

    def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, str]:
        """Simple Trusted Twin REST API calling routine. Interface is similar to requests.request method."""
        _args = (urllib.parse.quote(_arg, safe="") for _arg in args)
        _url = self.url.format(*_args)
        _headers = self.headers.copy() | kwargs.pop("headers", {})

        _dict = kwargs.pop("dictionary", None)
        if _dict is not None:
            _headers[_TT_DICT_HEADER] = b64encode(json.dumps(_dict).encode('utf-8')).decode('utf-8')

        _json = kwargs.pop("json", None) or kwargs.pop("body", None)

        _retries = kwargs.pop('retries', _TT_RETRIES)

        for _retry in range(_retries):
            _response = self._http_routine(self.method, _url, headers=_headers, json=_json, **kwargs)

            if _response.status_code < 500:
                break
            else:
                logger.info(_LOG_TEMPLATE, _retry + 1, _url, _response.status_code, _response.text)

                sleep(_TT_RETRIES_SLEEP)

        if self.codes is not None:
            try:
                self.codes[_response.status_code] += 1
            except KeyError:
                self.codes[_response.status_code] = 1

        return _response.status_code, _response.text


class TTRESTService(TTRESTServiceBase):
    """Trusted Twin synchronous REST client."""
    _endpoint_type = TTSyncEndpoint
