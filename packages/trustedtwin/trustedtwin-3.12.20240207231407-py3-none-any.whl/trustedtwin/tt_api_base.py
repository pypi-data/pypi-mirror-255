"""Trusted Twin API call library"""
import logging
import json

from typing import Any, Dict, Tuple, Optional, Union
from base64 import b64encode

# tt_endpoints is generated automatically
from trustedtwin.tt_endpoints import ENDPOINTS

logger = logging.getLogger(__name__)

# Number of tries before failure
_TT_RETRIES = 5
_TT_RETRIES_SLEEP = 2

# Logger message
_LOG_TEMPLATE = "TrustedTwin REST API call failed: Attempt=[%d], URL=[%s], Code=[%d], Response=[%s]."

# TrustedTwin headers
_TT_DICT_HEADER = 'X-TrustedTwin'
_TT_AUTH_HEADER = "Authorization"


class TTEndpointBase:
    """Trusted Twin endpoint base."""

    def __init__(self, method: str, url: str, headers: Dict, session: Optional[Any] = None, codes: Optional[Dict] = None) -> None:
        """Base class init."""
        self.method = method
        self.url = url
        self.headers = headers
        self.session = session
        self.codes = codes

    def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, str]:
        raise NotImplementedError


class TTRESTServiceBase:
    """Trusted Twin REST client base."""
    _endpoint_type = TTEndpointBase

    def __init__(
        self,
        tt_auth: Optional[str] = None,
        tt_base: Optional[str] = None,
        tt_dict: Optional[Dict] = None,
        session: Optional[Any] = None,
        codes: Optional[Dict] = None,
    ) -> None:
        self._headers = {
            'Content-Type': "application/json"
        }

        if tt_auth:
            self._headers[_TT_AUTH_HEADER] = tt_auth

        if tt_dict is not None:
            self._headers[_TT_DICT_HEADER] = b64encode(json.dumps(tt_dict).encode('utf-8')).decode('utf-8')

        self._base = tt_base or 'https://rest.trustedtwin.com'
        self._session = session
        self._codes = codes

        self._cache = {}

        assert issubclass(self._endpoint_type, TTEndpointBase), "ASSERT 0dc15258-8569-4bba-89a2-fa5f255431e4"
        assert isinstance(self._codes, (type(None), Dict)), "ASSERT 976039b6-431d-4120-bec0-1b7a3fd84eec"

    def __getattr__(self, name: str) -> Union[TTEndpointBase, Any]:
        if name in ENDPOINTS:
            _endpoint = self._cache.get(name, None)

            if _endpoint is None:
                _method, _url = ENDPOINTS[name]
                _endpoint = self._endpoint_type(
                    method=_method,
                    url=self._base + _url,
                    headers=self._headers,
                    session=self._session,
                    codes=self._codes
                )

                self._cache[name] = _endpoint

            return _endpoint

        return super().__getattribute__(name)
