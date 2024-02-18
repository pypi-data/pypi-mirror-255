"""Async extension for Trusted Twin API call library"""
import logging
import asyncio
import aiohttp
import json
import urllib

from typing import Any, Dict, Tuple, Optional, cast
from base64 import b64encode

from trustedtwin.tt_api_base import TTEndpointBase, TTRESTServiceBase, _TT_RETRIES, _TT_RETRIES_SLEEP, _TT_DICT_HEADER, _LOG_TEMPLATE

logger = logging.getLogger(__name__)


class TTAsyncEndpoint(TTEndpointBase):
    """Trusted Twin async endpoint (uses aiohttp request or session)."""

    def __init__(self, method: str, url: str, headers: Dict, session: Optional[aiohttp.ClientSession] = None, codes: Optional[Dict] = None) -> None:
        super().__init__(method, url, headers, session, codes)

        if not isinstance(session, aiohttp.ClientSession):
            self._http_routine = aiohttp.request
        else:
            self._http_routine = cast(aiohttp.ClientSession, self.session).request

    async def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, str]:
        """Simple Trusted Twin REST API calling routine. Interface is similar to aiohttp.request method."""
        _args = (urllib.parse.quote(_arg) for _arg in args)
        _url = self.url.format(*_args)
        _headers = self.headers.copy() | kwargs.pop("headers", {})

        _dict = kwargs.pop("dictionary", None)
        if _dict is not None:
            _headers[_TT_DICT_HEADER] = b64encode(json.dumps(_dict).encode('utf-8')).decode('utf-8')

        _json = kwargs.pop("json", None) or kwargs.pop("body", None)

        _retries = kwargs.pop('retries', _TT_RETRIES)

        for _retry in range(_retries):
            async with self._http_routine(self.method, _url, headers=_headers, json=_json, **kwargs) as _response:
                if _response.status < 500 or not _retries:
                    if self.codes is not None:
                        try:
                            self.codes[_response.status] += 1
                        except KeyError:
                            self.codes[_response.status] = 1

                    return _response.status, await _response.text()

                logger.info(_LOG_TEMPLATE, _retry + 1, _url, _response.status, await _response.text())

            await asyncio.sleep(_TT_RETRIES_SLEEP)


class TTAsyncRESTService(TTRESTServiceBase):
    """Trusted Twin async REST client."""
    _endpoint_type = TTAsyncEndpoint
