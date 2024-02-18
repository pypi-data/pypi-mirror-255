"""
This files contains definitions of TT API client interfaces. This code is automatically generated.
Generated for TT API specification version 3.12.00
"""

from typing import Optional, Any, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from trustedtwin.tt_api_base import TTEndpointBase, TTRESTServiceBase

TTEndpointBase: "TTEndpointBase"
TTRESTServiceBase: "TTRESTServiceBase"

class TTRESTService:
    """Sync TT API Client"""

    def __init__(
        self,
        tt_auth: str,
        tt_base: Optional[str] = None,
        tt_dict: Optional[Dict] = None,
        session: Optional[Any] = None,
        codes: Optional[Dict] = None,
    ) -> None:
        """Initialize object"""
    def get_account(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_account`` API operation.

        Calls: ``GET /account``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_account()
            >>> status
            200 (int)
            >>> text
            {
                "resource_access_log": null,
                "uuid": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123
            } (str)

        """
    def update_account(
        self, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_account`` API operation.

        Calls: ``PATCH /account``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "resource_access_log": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_account()
            >>> status
            200 (int)
            >>> text
            {
                "resource_access_log": null,
                "uuid": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123
            } (str)

        """
    def get_batches(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_batches`` API operation.

        Calls: ``GET /batches``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_batches()
            >>> status
            200 (int)
            >>> text
            {
                "batches": "None"
            } (str)

        """
    def create_batch(
        self, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_batch`` API operation.

        Calls: ``POST /batches``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "operation": null,
                "handler": null,
                "hash": null,
                "batch_dict": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_batch()
            >>> status
            201 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123,
                "batch": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def get_batch(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_batch`` API operation.

        Calls: ``GET /batches/{}``

        :param args: batch - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "download": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_batch('dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d')
            >>> status
            200 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123,
                "download": {
                    "url": "https://some_path.rest.trustedtwin.com/e544230b-cf65",
                    "validity_ts": 213423423560.123
                }
            } (str)

        """
    def delete_batch(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_batch`` API operation.

        Calls: ``DELETE /batches/{}``

        :param args: batch - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_batch('dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d')
            >>> status
            200 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123
            } (str)

        """
    def update_batch(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_batch`` API operation.

        Calls: ``PATCH /batches/{}``

        :param args: batch - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "status": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_batch('dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d')
            >>> status
            200 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123
            } (str)

        """
    def trace(self, dictionary: Optional[Dict] = None, **kwargs) -> Tuple[int, str]:
        """Executes ``trace`` API operation.

        Calls: ``POST /trace``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.trace()
            >>> status
            201 (int)
            >>> text
            {} (str)

        """
    def who_am_i(self, dictionary: Optional[Dict] = None, **kwargs) -> Tuple[int, str]:
        """Executes ``who_am_i`` API operation.

        Calls: ``GET /whoami``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.who_am_i()
            >>> status
            200 (int)
            >>> text
            {
                "account": "d88dfcb6-2e03-4e1e-b25a-96b1312f485c",
                "user": "f9b343a1-db99-4605-a200-873978517c15",
                "role": "96a290b9-a31b-441b-a98e-a0d17ba2bba9"
            } (str)

        """
    def get_users(self, dictionary: Optional[Dict] = None, **kwargs) -> Tuple[int, str]:
        """Executes ``get_users`` API operation.

        Calls: ``GET /users``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_users()
            >>> status
            200 (int)
            >>> text
            {
                "users": {
                    "ffc6ecf4-6de3-4174-a019-4dc65354a0f9": {
                        "name": "User A",
                        "role": "93099708-a399-4350-b414-f28cd52c39f5"
                    }
                }
            } (str)

        """
    def create_user(
        self, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_user`` API operation.

        Calls: ``POST /users``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "name": "first_user",
                "role": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "description": {
                    "custom_field": "custom_value"
                },
                "activity": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_user()
            >>> status
            201 (int)
            >>> text
            {
                "uuid": "644524db2-fcfe-4f36-bdd7-7309cb743e35",
                "role": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "account": "434524db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "first_user",
                "description": {
                    "custom_field": "custom_value"
                },
                "activity": null,
                "created_ts": 234324323333.23,
                "updated_ts": 345345345.345
            } (str)

        """
    def get_user(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_user`` API operation.

        Calls: ``GET /users/{}``

        :param args: user - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_user('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "uuid": "644524db2-fcfe-4f36-bdd7-7309cb743e35",
                "role": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "account": "434524db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "first_user",
                "description": {
                    "custom_field": "custom_value"
                },
                "activity": null,
                "created_ts": 234324323333.23,
                "updated_ts": 345345345.345
            } (str)

        """
    def delete_user(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_user`` API operation.

        Calls: ``DELETE /users/{}``

        :param args: user - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_user('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "uuid": "644524db2-fcfe-4f36-bdd7-7309cb743e35",
                "role": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "account": "434524db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "first_user",
                "description": {
                    "custom_field": "custom_value"
                },
                "activity": null,
                "created_ts": 234324323333.23,
                "updated_ts": 345345345.345
            } (str)

        """
    def update_user(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_user`` API operation.

        Calls: ``PATCH /users/{}``

        :param args: user - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "name": "Updated_user_name",
                "role": "1a624db2-fcfe-4f36-bdd7-7309cb743e55",
                "description": {
                    "custom_field": "updated_value"
                },
                "activity": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_user('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "name": "Updated_user_name",
                "role": "1a624db2-fcfe-4f36-bdd7-7309cb743e55",
                "description": {
                    "custom_field": "updated_value"
                },
                "activity": null
            } (str)

        """
    def get_user_secret(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_user_secret`` API operation.

        Calls: ``GET /users/{}/secrets``

        :param args: user - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_user_secret('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "account": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "user": "a998214a-e13d-412b-ffd6-911ab58c8883",
                "validity_ts": 1608592500.123,
                "created_ts": 1608591123.123,
                "updated_ts": 1608591123.123,
                "fingerprint": "HrwA"
            } (str)

        """
    def create_user_secret_pin(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_user_secret_pin`` API operation.

        Calls: ``POST /users/{}/secrets``

        :param args: user - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "validity_ts": 1608591121.123
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_user_secret_pin('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            201 (int)
            >>> text
            {
                "pin": "AVC110"
            } (str)

        """
    def delete_user_secret(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_user_secret`` API operation.

        Calls: ``DELETE /users/{}/secrets``

        :param args: user - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_user_secret('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "account": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "user": "a998214a-e13d-412b-ffd6-911ab58c8883",
                "validity_ts": 1608592500.123,
                "created_ts": 1608591123.123,
                "updated_ts": 1608591123.123,
                "fingerprint": "HrwA"
            } (str)

        """
    def update_user_secret(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_user_secret`` API operation.

        Calls: ``PATCH /users/{}/secrets``

        :param args: user - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "validity_ts": 1643641310.027
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_user_secret('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            201 (int)
            >>> text
            {
                "account": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "user": "a998214a-e13d-412b-ffd6-911ab58c8883",
                "validity_ts": 1608592500.123,
                "created_ts": 1608591123.123,
                "updated_ts": 1608591123.123,
                "fingerprint": "HrwA"
            } (str)

        """
    def create_user_secret(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_user_secret`` API operation.

        Calls: ``POST /secrets/{}/{}``

        :param args: account, pin - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_user_secret('a6dc7ec3-0bff-4bb8-aadd-d4e6773cc860', 'a3ks41')
            >>> status
            201 (int)
            >>> text
            {
                "account": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "user": "a998214a-e13d-412b-ffd6-911ab58c8883",
                "secret": "kxjCrGbjTC9rLHAMkSWpozreJfdRtsiv/E46fUxvcuwqapdNRnXQptIngRKyHrwA",
                "validity_ts": 1608592500.123,
                "created_ts": 1608591123.123,
                "updated_ts": 1608591123.123
            } (str)

        """
    def create_user_token(
        self, body: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_user_token`` API operation.

        Calls: ``POST /token``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "secret_dict": {
                    "key1": 123,
                    "key2": "some string"
                },
                "options": "None",
                "validity_ts": 1608591123.123
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_user_token()
            >>> status
            201 (int)
            >>> text
            {
                "token": "kxjCrGbjTC9rLHAMkSWpozreJfdRtsiv/E46fUxvcuwqapdNRnXQptIngRKyHrwA",
                "options": "None",
                "validity_ts": 1608591123.123
            } (str)

        """
    def refresh_user_token(
        self, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``refresh_user_token`` API operation.

        Calls: ``POST /token/refresh``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "validity_ts": 1608591123.123
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.refresh_user_token()
            >>> status
            201 (int)
            >>> text
            {
                "token": "kxjCrGbjTC9rLHAMkSWpozreJfdRtsiv/E46fUxvcuwqapdNRnXQptIngRKyHrwA",
                "validity_ts": 1708591123.123
            } (str)

        """
    def get_user_roles(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_user_roles`` API operation.

        Calls: ``GET /roles``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_user_roles()
            >>> status
            200 (int)
            >>> text
            {
                "roles": {
                    "3d4c3ec0-6c5f-4d32-ab23-4df8c69f142c": {
                        "name": "Read only",
                        "created_ts": "1646307775.089,",
                        "updated_ts": 1646307775.089
                    },
                    "cba1a586-b5b9-46f5-a99b-76f70404508f": {
                        "name": "Administrator",
                        "created_ts": "1646307910.852,",
                        "updated_ts": 1646307910.852
                    }
                }
            } (str)

        """
    def create_user_role(
        self, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_user_role`` API operation.

        Calls: ``POST /roles``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "name": "role_1",
                "statement": {
                    "effect": "allow",
                    "actions": "None"
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_user_role()
            >>> status
            201 (int)
            >>> text
            {
                "uuid": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "role_1",
                "account": "1cbaed97-dca3-4929-a23b-fff8e755fadd",
                "statement": {
                    "effect": "allow",
                    "actions": [
                        "create_twin",
                        "get_twin"
                    ]
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                },
                "created_ts": 234324323333.44,
                "updated_ts": 234324323333.44
            } (str)

        """
    def get_user_role(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_user_role`` API operation.

        Calls: ``GET /roles/{}``

        :param args: role - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_user_role('5a298144-c5d7-4802-a7bc-127168280ca2')
            >>> status
            200 (int)
            >>> text
            {
                "uuid": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "role_1",
                "account": "1cbaed97-dca3-4929-a23b-fff8e755fadd",
                "statement": {
                    "effect": "allow",
                    "actions": [
                        "create_twin",
                        "get_twin"
                    ]
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                },
                "created_ts": 234324323333.44,
                "updated_ts": 234324323333.44
            } (str)

        """
    def delete_user_role(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_user_role`` API operation.

        Calls: ``DELETE /roles/{}``

        :param args: role - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_user_role('5a298144-c5d7-4802-a7bc-127168280ca2')
            >>> status
            200 (int)
            >>> text
            {
                "uuid": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "role_1",
                "account": "1cbaed97-dca3-4929-a23b-fff8e755fadd",
                "statement": {
                    "effect": "allow",
                    "actions": [
                        "create_twin",
                        "get_twin"
                    ]
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                },
                "created_ts": 234324323333.44,
                "updated_ts": 234324323333.44
            } (str)

        """
    def update_user_role(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_user_role`` API operation.

        Calls: ``PATCH /roles/{}``

        :param args: role - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "name": "role_1",
                "statement": {
                    "effect": "allow",
                    "actions": [
                        "create_twin",
                        "get_twin",
                        "get_twin_identities"
                    ]
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_user_role('5a298144-c5d7-4802-a7bc-127168280ca2')
            >>> status
            201 (int)
            >>> text
            {
                "uuid": "43624db2-fcfe-4f36-bdd7-7309cb743e35",
                "name": "role_1",
                "account": "1cbaed97-dca3-4929-a23b-fff8e755fadd",
                "statement": {
                    "effect": "allow",
                    "actions": [
                        "create_twin",
                        "get_twin"
                    ]
                },
                "rules": {
                    "twin_rule": "TWIN.company == USER.company",
                    "entry_rule": null,
                    "identity_rule": null
                },
                "created_ts": 234324323333.44,
                "updated_ts": 234324323333.44
            } (str)

        """
    def resolve_twin_identity(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``resolve_twin_identity`` API operation.

        Calls: ``GET /resolve/{}``

        :param args: identity - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "context": null,
                "details": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.resolve_twin_identity('RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245')
            >>> status
            200 (int)
            >>> text
            {
                "twins": [
                    "796150db-3e32-4195-80df-fdb0cca4b635",
                    "9d303912-6eda-4f92-8c9a-2bb3e1f7dafc"
                ]
            } (str)

        """
    def scan_twins(
        self, params: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``scan_twins`` API operation.

        Calls: ``GET /twins``

        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "cursor": null,
                "count": null,
                "match": "LEDGER.serial > 3",
                "details": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.scan_twins()
            >>> status
            200 (int)
            >>> text
            {
                "cursor": "YzY3M2E2ZDAtZmZhNi00MDdiLWI4NGQtZTMyODNmMWRiNzg3",
                "twins": [
                    "7cb4e946-7015-4623-a335-5ee52972c858",
                    "41bbd69e-c5b3-4383-9c64-0321367673b8",
                    "1b64a1da-3aaf-486a-af5d-685bdeb82ca9"
                ]
            } (str)

        """
    def create_twin(
        self, body: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_twin`` API operation.

        Calls: ``POST /twins``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_twin()
            >>> status
            201 (int)
            >>> text
            {
                "status": "alive",
                "owner": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "updated_ts": 204543545345.123,
                "creation_certificate": {
                    "uuid": "cf684c35-200e-4936-8b63-e6e51b6e3569",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            } (str)

        """
    def get_twin(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin`` API operation.

        Calls: ``GET /twins/{}``

        :param args: twin - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "show_terminated": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "status": "alive",
                "owner": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "updated_ts": 1608591121.123,
                "description": {
                    "key1": 123,
                    "key2": "some string"
                },
                "creation_certificate": {
                    "uuid": "cf684c35-200e-4936-8b63-e6e51b6e3569",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                }
            } (str)

        """
    def terminate_twin(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``terminate_twin`` API operation.

        Calls: ``DELETE /twins/{}``

        :param args: twin - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.terminate_twin('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "status": "alive",
                "owner": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "updated_ts": 204543545345.123,
                "creation_certificate": {
                    "uuid": "cf684c35-200e-4936-8b63-e6e51b6e3569",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "termination_certificate": {
                    "issuer": "e8659552-e63c-401b-aad6-919a458c8733",
                    "terminated_ts": 1608591133
                },
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            } (str)

        """
    def update_twin(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_twin`` API operation.

        Calls: ``PATCH /twins/{}``

        :param args: twin - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_twin('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "status": "alive",
                "owner": "e834214a-e13d-412b-ffd6-911ab58c8733",
                "updated_ts": 204543545345.123,
                "creation_certificate": {
                    "uuid": "cf684c35-200e-4936-8b63-e6e51b6e3569",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            } (str)

        """
    def get_twin_identities(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_identities`` API operation.

        Calls: ``GET /twins/{}/identities``

        :param args: twin - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "show_expired": null,
                "show_valid": null,
                "show_foreign": null,
                "show_public": null,
                "show_private": null,
                "show_personal": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_identities('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "identities": {
                    "RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bde": {
                        "validity_ts": 1646302849.877,
                        "created_ts": 1646302849.877,
                        "updated_ts": 1646302849.877
                    }
                }
            } (str)

        """
    def create_twin_identity(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_twin_identity`` API operation.

        Calls: ``POST /twins/{}/identities``

        :param args: twin - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "identities": {
                    "RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bde": {
                        "validity_ts": 1608591123.123,
                        "visibility": "USER.profession == 'accounting'"
                    },
                    "NFC#6c02a13e-cbac-473d-982c-807c2e7cfb7c": {
                        "validity_ts": 32482309480294.12
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_twin_identity('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            201 (int)
            >>> text
            {
                "identities": null
            } (str)

        """
    def get_twin_identity(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_identity`` API operation.

        Calls: ``GET /twins/{}/identities/{}``

        :param args: twin, identity - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_identity('085c0f9f-427e-4e23-9a60-bacf6585a862', 'RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245')
            >>> status
            200 (int)
            >>> text
            {
                "validity_ts": 1608591123.123,
                "visibility": "USER.profession == 'accounting'",
                "updated_ts": 1608591123.123,
                "creation_certificate": {
                    "created_ts": 1608591000.123,
                    "creator": "e834214a-e13d-412b-ffd6-911ab58c8733",
                    "identity": "RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245"
                }
            } (str)

        """
    def delete_twin_identity(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_twin_identity`` API operation.

        Calls: ``DELETE /twins/{}/identities/{}``

        :param args: twin, identity - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_twin_identity('085c0f9f-427e-4e23-9a60-bacf6585a862', 'RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245')
            >>> status
            200 (int)
            >>> text
            {
                "validity_ts": 1608591123.123,
                "visibility": "USER.profession == 'accounting'",
                "updated_ts": 1608591123.123,
                "creation_certificate": {
                    "created_ts": 1608591000.123,
                    "creator": "e834214a-e13d-412b-ffd6-911ab58c8733",
                    "identity": "RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245"
                }
            } (str)

        """
    def update_twin_identity(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_twin_identity`` API operation.

        Calls: ``PATCH /twins/{}/identities/{}``

        :param args: twin, identity - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "validity_ts": 1608591123.123,
                "visibility": "USER.profession == 'accounting'"
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_twin_identity('085c0f9f-427e-4e23-9a60-bacf6585a862', 'RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245')
            >>> status
            201 (int)
            >>> text
            {
                "validity_ts": 1608591123.123,
                "visibility": "USER.profession == 'accounting'",
                "updated_ts": 1608591123.123,
                "creation_certificate": {
                    "created_ts": 1608591000.123,
                    "creator": "e834214a-e13d-412b-ffd6-911ab58c8733",
                    "identity": "RFID#be744bdc-0f6d-4a00-8199-9f6a893c1bd245"
                }
            } (str)

        """
    def get_twin_ledger_entry(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_ledger_entry`` API operation.

        Calls: ``GET /twins/{}/ledgers/{}``

        :param args: twin, ledger - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "show_references": null,
                "show_public": null,
                "show_private": null,
                "entries": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_ledger_entry('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "key1": {
                        "value": 123,
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "status": "ok"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key3": {
                        "include": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/foreign_key"
                        },
                        "value": "foreign_value",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def add_twin_ledger_entry(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``add_twin_ledger_entry`` API operation.

        Calls: ``POST /twins/{}/ledgers/{}``

        :param args: twin, ledger - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "entries": {
                    "key1": {
                        "value": 123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "visibility": "USER.profession == 'accounting'"
                        }
                    },
                    "key3": {
                        "value": 345,
                        "history": "3M",
                        "timeseries": {
                            "timeseries_table_name_1": {
                                "measurement": "{entry_name}",
                                "dimensions": {
                                    "dim_name_1": "{LEDGER[serial]}"
                                }
                            },
                            "timeseries_table_name_2": {}
                        }
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.add_twin_ledger_entry('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            201 (int)
            >>> text
            {
                "entries": {
                    "key1": {
                        "value": 123,
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "status": "ok"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key3": {
                        "include": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/foreign_key"
                        },
                        "value": "foreign_value",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def delete_twin_ledger_entry(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_twin_ledger_entry`` API operation.

        Calls: ``DELETE /twins/{}/ledgers/{}``

        :param args: twin, ledger - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "entries": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_twin_ledger_entry('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "key1": {
                        "value": 123,
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "status": "ok"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key3": {
                        "include": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/foreign_key"
                        },
                        "value": "foreign_value",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 534543545345.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def update_twin_ledger_entry(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_twin_ledger_entry`` API operation.

        Calls: ``PATCH /twins/{}/ledgers/{}``

        :param args: twin, ledger - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "entries": {
                    "key1": {
                        "value": 456
                    },
                    "key2": {
                        "visibility": "USER.profession == 'accounting'"
                    },
                    "key3": {
                        "visibility": "USER.profession == 'accounting'"
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_twin_ledger_entry('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "key1": {
                        "value": 456,
                        "visibility": "public",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 232342342234.123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "status": "ok"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key3": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/foreign_key"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def get_twin_ledger_entry_value(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_ledger_entry_value`` API operation.

        Calls: ``GET /twins/{}/ledgers/{}/value``

        :param args: twin, ledger - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "entries": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_ledger_entry_value('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "entry_1": {
                        "value": "123",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 213423423424.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def update_twin_ledger_entry_value(
        self, *args, body: Dict, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_twin_ledger_entry_value`` API operation.

        Calls: ``PATCH /twins/{}/ledgers/{}/value``

        :param args: twin, ledger - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body::

            {
                "entries": {
                    "key1": {
                        "value": 456
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_twin_ledger_entry_value('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "key1": {
                        "value": 456,
                        "visibility": "public",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 232342342234.123
                    },
                    "key2": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/e834214a-e13d-412b-ffd6-911ab58c8733/foreign_key",
                            "status": "ok"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 204543545345.123
                    },
                    "key3": {
                        "ref": {
                            "source": "twin://77f57a6e-1026-4272-8301-2a4419f32daa/foreign_key"
                        },
                        "value": "foreign_value",
                        "visibility": "USER.profession == 'accounting'",
                        "entry_created_ts": 213423423424.123,
                        "entry_updated_ts": 232342342234.123,
                        "value_changed_ts": 204543545345.123
                    }
                }
            } (str)

        """
    def get_twin_ledger_entry_history(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_ledger_entry_history`` API operation.

        Calls: ``GET /twins/{}/ledgers/{}/history``

        :param args: twin, ledger - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "le": null,
                "ge": null,
                "limit": null,
                "entries": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_ledger_entry_history('085c0f9f-427e-4e23-9a60-bacf6585a862', '902f36e1-f401-419d-b081-6312f7168ef9')
            >>> status
            200 (int)
            >>> text
            {
                "entries": {
                    "entry_1": {
                        "1650882205.34": "abc",
                        "1650882204.34": "cde"
                    },
                    "entry_2": "Entry not accessible."
                }
            } (str)

        """
    def get_twin_docs(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_docs`` API operation.

        Calls: ``GET /twins/{}/docs``

        :param args: twin - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "mask": null,
                "view": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_docs('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "docs": {
                    "file_name_0.txt": [
                        234234234.343,
                        23423423423.333,
                        23
                    ]
                }
            } (str)

        """
    def attach_twin_doc(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``attach_twin_doc`` API operation.

        Calls: ``POST /twins/{}/docs``

        :param args: twin - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "docs": {
                    "Certifications/certification_2022_v1.txt": {
                        "handler": "a7fbcd7c-50a7-4df5-a6e5-416559ae24ae",
                        "storage_class": "access_optimized",
                        "description": {
                            "title": "instructions_2022_v1",
                            "author": "Ana Ramos"
                        }
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.attach_twin_doc('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            201 (int)
            >>> text
            {
                "docs": {
                    "Certifications/certification_2022_v1.txt": {
                        "handler": "a7fbcd7c-50a7-4df5-a6e5-416559ae24ae",
                        "storage_class": "access_optimized",
                        "description": {
                            "title": "instructions_2022_v1",
                            "author": "Ana Ramos"
                        }
                    }
                }
            } (str)

        """
    def delete_twin_docs(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_twin_docs`` API operation.

        Calls: ``DELETE /twins/{}/docs``

        :param args: twin - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_twin_docs('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "docs": {
                    "file_name_0.txt": [
                        234234234.343,
                        23423423423.333,
                        23
                    ]
                }
            } (str)

        """
    def get_twin_doc(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_twin_doc`` API operation.

        Calls: ``GET /twins/{}/docs/{}``

        :param args: twin, doc_name - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "download": null,
                "validity_ts": 1608591123
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_twin_doc('085c0f9f-427e-4e23-9a60-bacf6585a862', 'example.txt')
            >>> status
            200 (int)
            >>> text
            {
                "creation_certificate": {
                    "size": 10000,
                    "hash": "some_calculated_hash",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "storage_class": null,
                "updated_ts": 213423423560.123,
                "description": {
                    "key1": 123,
                    "key2": "some string"
                },
                "status": null,
                "download": {
                    "url": "https://some_path.rest.trustedtwin.com/e544230b-cf65",
                    "validity_ts": 213423423560.123
                }
            } (str)

        """
    def delete_twin_doc(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_twin_doc`` API operation.

        Calls: ``DELETE /twins/{}/docs/{}``

        :param args: twin, doc_name - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_twin_doc('085c0f9f-427e-4e23-9a60-bacf6585a862', 'example.txt')
            >>> status
            200 (int)
            >>> text
            {
                "creation_certificate": {
                    "size": 10000,
                    "hash": "some_calculated_hash",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "storage_class": null,
                "updated_ts": 213423423560.123,
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            } (str)

        """
    def update_twin_doc(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_twin_doc`` API operation.

        Calls: ``PATCH /twins/{}/docs/{}``

        :param args: twin, doc_name - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "description": {
                    "key1": 123,
                    "key2": "some string"
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_twin_doc('085c0f9f-427e-4e23-9a60-bacf6585a862', 'example.txt')
            >>> status
            200 (int)
            >>> text
            {
                "creation_certificate": {
                    "size": 10000,
                    "hash": "some_calculated_hash",
                    "created_ts": 1608591121.123,
                    "creator": "e8659552-e63c-401b-aad6-919a458c8733"
                },
                "storage_class": null,
                "updated_ts": 213423423560.123,
                "description": {
                    "key1": 123,
                    "key2": "some string"
                },
                "status": "ok"
            } (str)

        """
    def download_doc(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``download_doc`` API operation.

        Calls: ``GET /download/{}/{}``

        :param args: account, handler - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.download_doc('a6dc7ec3-0bff-4bb8-aadd-d4e6773cc860', 'c803382b-f175-4e36-b807-b08651d3d297-1688480283')
            >>> status
            200 (int)
            >>> text
            {} (str)

        """
    def create_upload_url(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_upload_url`` API operation.

        Calls: ``POST /cache``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_upload_url()
            >>> status
            201 (int)
            >>> text
            {
                "handler": "87624db2-fcfe-4f36-bdd7-7309cb74be3b",
                "url": "https://some.upload.url",
                "validity_ts": 213423423560.123
            } (str)

        """
    def invalidate_upload_url(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``invalidate_upload_url`` API operation.

        Calls: ``DELETE /cache/{}``

        :param args: handler - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.invalidate_upload_url('c803382b-f175-4e36-b807-b08651d3d297-1688480283')
            >>> status
            200 (int)
            >>> text
            {
                "handler": "87624db2-fcfe-4f36-bdd7-7309cb74be3b"
            } (str)

        """
    def get_databases(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_databases`` API operation.

        Calls: ``GET /account/services/databases``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_databases()
            >>> status
            200 (int)
            >>> text
            {
                "default": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "databases": null
            } (str)

        """
    def get_database(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_database`` API operation.

        Calls: ``GET /account/services/databases/{}``

        :param args: database - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_database('None')
            >>> status
            200 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123,
                "note": null,
                "instance_type": null,
                "uuid": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "database_size": 32032768,
                "default": null
            } (str)

        """
    def update_database(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_database`` API operation.

        Calls: ``PATCH /account/services/databases/{}``

        :param args: database - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "default": null,
                "note": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_database('None')
            >>> status
            200 (int)
            >>> text
            {
                "status": null,
                "created_ts": 1663753700.123,
                "updated_ts": 1663753700.123,
                "note": null,
                "instance_type": null,
                "uuid": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "database_size": 32032768,
                "default": null
            } (str)

        """
    def get_database_access(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_database_access`` API operation.

        Calls: ``GET /account/services/databases/{}/access``

        :param args: database - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_database_access('None')
            >>> status
            200 (int)
            >>> text
            {
                "ips": null,
                "users": null
            } (str)

        """
    def update_database_user_access(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_database_user_access`` API operation.

        Calls: ``PATCH /account/services/databases/{}/access/users/{}``

        :param args: database, user - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "timeseries": "None",
                "indexes": "None",
                "customer_data": "None"
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_database_user_access('None', '7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "timeseries": "None",
                "indexes": "None",
                "customer_data": "None"
            } (str)

        """
    def get_timeseries_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_timeseries_table`` API operation.

        Calls: ``GET /account/services/timeseries/{}``

        :param args: timeseries - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_timeseries_table('test_timeseries_table_name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "dimensions": {
                    "names": "None",
                    "types": "None"
                },
                "measurements": {
                    "names": "None",
                    "types": "None"
                },
                "defaults": {
                    "measurement": "{entry_name}",
                    "dimensions": null
                },
                "retention": "3M",
                "chunk": "7D",
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def delete_timeseries_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_timeseries_table`` API operation.

        Calls: ``DELETE /account/services/timeseries/{}``

        :param args: timeseries - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_timeseries_table('test_timeseries_table_name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "dimensions": {
                    "names": "None",
                    "types": "None"
                },
                "measurements": {
                    "names": "None",
                    "types": "None"
                },
                "defaults": {
                    "measurement": "{entry_name}",
                    "dimensions": null
                },
                "retention": "3M",
                "chunk": "7D",
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def update_timeseries_table(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_timeseries_table`` API operation.

        Calls: ``PATCH /account/services/timeseries/{}``

        :param args: timeseries - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "defaults": {
                    "measurement": "{entry_name}",
                    "dimensions": null
                },
                "retention": "3M",
                "chunk": "7D",
                "dimensions": {
                    "names": "None",
                    "types": "None"
                },
                "measurements": {
                    "names": "None",
                    "types": "None"
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_timeseries_table('test_timeseries_table_name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "dimensions": {
                    "names": "None",
                    "types": "None"
                },
                "measurements": {
                    "names": "None",
                    "types": "None"
                },
                "defaults": {
                    "measurement": "{entry_name}",
                    "dimensions": null
                },
                "retention": "3M",
                "chunk": "7D",
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def get_timeseries_tables(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_timeseries_tables`` API operation.

        Calls: ``GET /account/services/timeseries``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_timeseries_tables()
            >>> status
            200 (int)
            >>> text
            {
                "timeseries": "None"
            } (str)

        """
    def create_timeseries_table(
        self, body: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_timeseries_table`` API operation.

        Calls: ``POST /account/services/timeseries``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "timeseries": {
                    "environmental_data": {
                        "dimensions": {
                            "name": [
                                "city"
                            ],
                            "types": [
                                "varchar"
                            ]
                        },
                        "measurements": {
                            "names": [
                                "temperature",
                                "ozone",
                                "relative_humidity"
                            ],
                            "types": [
                                "real",
                                "real",
                                "real"
                            ],
                            "defaults": {
                                "measurements": "temperature",
                                "dimensions": {
                                    "city": "Gdansk"
                                }
                            },
                            "retention": "3M",
                            "chunk": "1W"
                        }
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_timeseries_table()
            >>> status
            200 (int)
            >>> text
            {
                "timeseries": {
                    "environmental_data": {
                        "dimensions": {
                            "name": [
                                "city"
                            ],
                            "types": [
                                "varchar"
                            ]
                        },
                        "measurements": {
                            "names": [
                                "temperature",
                                "ozone",
                                "relative_humidity"
                            ],
                            "types": [
                                "real",
                                "real",
                                "real"
                            ],
                            "defaults": {
                                "measurements": "temperature",
                                "dimensions": {
                                    "city": "Gdansk"
                                }
                            },
                            "retention": "3M",
                            "chunk": "1W"
                        }
                    }
                }
            } (str)

        """
    def truncate_timeseries_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``truncate_timeseries_table`` API operation.

        Calls: ``DELETE /account/services/timeseries/{}/data``

        :param args: timeseries - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.truncate_timeseries_table('test_timeseries_table_name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "dimensions": {
                    "names": "None",
                    "types": "None"
                },
                "measurements": {
                    "names": "None",
                    "types": "None"
                },
                "defaults": {
                    "measurement": "{entry_name}",
                    "dimensions": null
                },
                "retention": "3M",
                "chunk": "7D",
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def get_log(
        self, params: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_log`` API operation.

        Calls: ``GET /log``

        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "fragment": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_log()
            >>> status
            200 (int)
            >>> text
            {
                "fragment": "6dd13315-207b-46ac-8e79-21f7e2c8787d",
                "messages": [
                    "Row potentially incomplete. Refer to reported errors: twin=[0d98b646-4944-4417-9a0d-8951aacbe186]."
                ]
            } (str)

        """
    def webhook_subscribe(
        self, body: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``webhook_subscribe`` API operation.

        Calls: ``POST /notifications/webhooks``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "callback_url": "https://example.com",
                "topic": "my_topic",
                "client_secret": 100,
                "expires": 120
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.webhook_subscribe()
            >>> status
            201 (int)
            >>> text
            {
                "subscription": {
                    "topic": "my_topic",
                    "account": "02bb52f9-6959-46ec-a075-1a1326c8eae7",
                    "validity_ts": 1608592501
                },
                "callback_url": "https://my-custom-url.com",
                "server_secret": 200
            } (str)

        """
    def webhook_confirm_subscription(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``webhook_confirm_subscription`` API operation.

        Calls: ``GET /notifications/webhooks/{}``

        :param args: account - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "token": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.webhook_confirm_subscription('a6dc7ec3-0bff-4bb8-aadd-d4e6773cc860')
            >>> status
            200 (int)
            >>> text
            {
                "topic": "my_topic",
                "account": "02bb52f9-6959-46ec-a075-1a1326c8eae7",
                "validity_ts": 1608592501,
                "unsubscribe_url": "https://rest.trustedtwin.com/notifications/webhooks/d6779760-effa-4d2b-a955-1fb4428af117?token=TOKEN",
                "refresh_url": "https://rest.trustedtwin.com/notifications/webhooks/d6779760-effa-4d2b-a955-1fb4428af117?token=TOKEN"
            } (str)

        """
    def webhook_unsubscribe(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``webhook_unsubscribe`` API operation.

        Calls: ``DELETE /notifications/webhooks/{}``

        :param args: account - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "token": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.webhook_unsubscribe('a6dc7ec3-0bff-4bb8-aadd-d4e6773cc860')
            >>> status
            201 (int)
            >>> text
            {
                "topic": "test-topic",
                "account": "c7f0e02e-6414-47ed-8dce-e027eb85275d",
                "validity_ts": 1608591121.123
            } (str)

        """
    def webhook_refresh_subscription(
        self,
        *args,
        params: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``webhook_refresh_subscription`` API operation.

        Calls: ``PATCH /notifications/webhooks/{}``

        :param args: account - positional arguments
        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "token": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.webhook_refresh_subscription('a6dc7ec3-0bff-4bb8-aadd-d4e6773cc860')
            >>> status
            201 (int)
            >>> text
            {
                "subscription": {
                    "topic": "my_topic",
                    "account": "02bb52f9-6959-46ec-a075-1a1326c8eae7",
                    "validity_ts": 1608592501,
                    "unsubscribe_url": "https://rest.trustedtwin.com/notifications/webhooks/d6779760-effa-4d2b-a955-1fb4428af117?token=TOKEN",
                    "refresh_url": "https://rest.trustedtwin.com/notifications/webhooks/d6779760-effa-4d2b-a955-1fb4428af117?token=TOKEN"
                },
                "callback_url": "https://my-custom-url.com"
            } (str)

        """
    def get_indexes_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_indexes_table`` API operation.

        Calls: ``GET /account/services/indexes/{}``

        :param args: index - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_indexes_table('index-name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "rule": "LEDGER.serial > 3",
                "properties": {
                    "names": [
                        "property_1",
                        "property_2"
                    ],
                    "types": [
                        "int",
                        "varchar"
                    ]
                },
                "templates": {
                    "properties": {
                        "property_1": "{LEDGER[serial]}",
                        "property_2": "{LEDGER[model]}"
                    }
                },
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def delete_indexes_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``delete_indexes_table`` API operation.

        Calls: ``DELETE /account/services/indexes/{}``

        :param args: index - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.delete_indexes_table('index-name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "rule": "LEDGER.serial > 3",
                "properties": {
                    "names": [
                        "property_1",
                        "property_2"
                    ],
                    "types": [
                        "int",
                        "varchar"
                    ]
                },
                "templates": {
                    "properties": {
                        "property_1": "{LEDGER[serial]}",
                        "property_2": "{LEDGER[model]}"
                    }
                },
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def update_indexes_table(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``update_indexes_table`` API operation.

        Calls: ``PATCH /account/services/indexes/{}``

        :param args: index - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "rule": "LEDGER.serial > 3",
                "properties": {
                    "names": [
                        "property_1",
                        "property_2"
                    ],
                    "types": [
                        "int",
                        "varchar"
                    ]
                },
                "templates": {
                    "properties": {
                        "property_1": "{LEDGER[serial]}",
                        "property_2": "{LEDGER[model]}"
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.update_indexes_table('index-name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "rule": "LEDGER.serial > 3",
                "properties": {
                    "names": [
                        "property_1",
                        "property_2"
                    ],
                    "types": [
                        "int",
                        "varchar"
                    ]
                },
                "templates": {
                    "properties": {
                        "property_1": "{LEDGER[serial]}",
                        "property_2": "{LEDGER[model]}"
                    }
                },
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def get_indexes_tables(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_indexes_tables`` API operation.

        Calls: ``GET /account/services/indexes``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_indexes_tables()
            >>> status
            200 (int)
            >>> text
            {
                "indexes": "None"
            } (str)

        """
    def create_indexes_table(
        self, body: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``create_indexes_table`` API operation.

        Calls: ``POST /account/services/indexes``

        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "indexes": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.create_indexes_table()
            >>> status
            201 (int)
            >>> text
            {
                "indexes": {
                    "index_table_1": {
                        "rule": "LEDGER.serial > 3",
                        "properties": {
                            "names": [
                                "property_1",
                                "property_2"
                            ],
                            "types": [
                                "int",
                                "varchar"
                            ]
                        },
                        "templates": {
                            "properties": {
                                "property_1": "{LEDGER[serial]}",
                                "property_2": "{LEDGER[model]}"
                            }
                        }
                    },
                    "index_table_2": {
                        "error": "Table already exists."
                    }
                }
            } (str)

        """
    def truncate_indexes_table(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``truncate_indexes_table`` API operation.

        Calls: ``DELETE /account/services/indexes/{}/data``

        :param args: index - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.truncate_indexes_table('index-name')
            >>> status
            200 (int)
            >>> text
            {
                "stats": {
                    "table_size": 8192,
                    "index_size": 24576,
                    "toast_size": 0,
                    "total_size": 32768
                },
                "rule": "LEDGER.serial > 3",
                "properties": {
                    "names": [
                        "property_1",
                        "property_2"
                    ],
                    "types": [
                        "int",
                        "varchar"
                    ]
                },
                "templates": {
                    "properties": {
                        "property_1": "{LEDGER[serial]}",
                        "property_2": "{LEDGER[model]}"
                    }
                },
                "database": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d"
            } (str)

        """
    def get_account_usage(
        self, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_account_usage`` API operation.

        Calls: ``GET /usage``

        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_account_usage()
            >>> status
            200 (int)
            >>> text
            {
                "usage": {
                    "2022-06-12-17": {
                        "l1_hit_count": 11.434,
                        "l2_hit_count": 22,
                        "l2_io_time": 123.234
                    }
                }
            } (str)

        """
    def get_user_usage(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_user_usage`` API operation.

        Calls: ``GET /usage/{}``

        :param args: user - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_user_usage('7b75d119-2d82-435b-9957-25c30cfee101')
            >>> status
            200 (int)
            >>> text
            {
                "usage": {
                    "2022-06-12-17": {
                        "l1_hit_count": 11.434,
                        "l2_hit_count": 22,
                        "l2_io_time": 123.234
                    }
                }
            } (str)

        """
    def get_stickers(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_stickers`` API operation.

        Calls: ``GET /twins/{}/stickers``

        :param args: twin - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_stickers('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            200 (int)
            >>> text
            {
                "accounts": {
                    "accounts": {
                        "9891264d-4a77-4fa2-ae7f-84c9af14ae3b": {
                            "red": {
                                "message": "Example Message",
                                "validity_ts": 1663753700.123,
                                "created_ts": 1664961051.357
                            }
                        }
                    }
                }
            } (str)

        """
    def put_sticker(
        self,
        *args,
        body: Optional[Dict] = None,
        dictionary: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[int, str]:
        """Executes ``put_sticker`` API operation.

        Calls: ``POST /twins/{}/stickers``

        :param args: twin - positional arguments
        :param body: Request body in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Body[Optional]::

            {
                "stickers": {
                    "red": {
                        "message": "Example Message",
                        "recipients": [
                            "3108f3bd-dcfa-48e6-8a32-c74241e1eb1d"
                        ],
                        "validity_ts": 1663753700.123,
                        "publish": "on_put | on_remove | on_expire"
                    }
                }
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.put_sticker('085c0f9f-427e-4e23-9a60-bacf6585a862')
            >>> status
            201 (int)
            >>> text
            {
                "stickers": null
            } (str)

        """
    def get_sticker(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``get_sticker`` API operation.

        Calls: ``GET /twins/{}/stickers/{}``

        :param args: twin, color - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.get_sticker('085c0f9f-427e-4e23-9a60-bacf6585a862', 'green')
            >>> status
            200 (int)
            >>> text
            {
                "message": "Any message for recipients ...",
                "recipients": [
                    "0e483b19-62bc-4862-8a14-2cb409232045",
                    "ea2eb0ff-155d-4a12-8ba6-df5b1e615131"
                ],
                "validity_ts": 1663753700.123,
                "created_ts": 1663753700.123,
                "publish": "on_put"
            } (str)

        """
    def remove_sticker(
        self, *args, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``remove_sticker`` API operation.

        Calls: ``DELETE /twins/{}/stickers/{}``

        :param args: twin, color - positional arguments
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.remove_sticker('085c0f9f-427e-4e23-9a60-bacf6585a862', 'green')
            >>> status
            200 (int)
            >>> text
            {
                "account": "dfe8e356-30a7-4b2c-bdfb-a7ae2c159f6d",
                "message": "Any message for recipients ...",
                "validity_ts": 1663753700.123,
                "created_ts": 1663753700.123
            } (str)

        """
    def list_stickers(
        self, params: Optional[Dict] = None, dictionary: Optional[Dict] = None, **kwargs
    ) -> Tuple[int, str]:
        """Executes ``list_stickers`` API operation.

        Calls: ``GET /stickers``

        :param params: Request query params in dict format.
        :param dictionary: Trusted Twin custom header dictionary.
        :param kwargs: data, json, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, stream, cert

        params::

            {
                "color": null,
                "context": null,
                "ge": null,
                "le": null,
                "limit": null,
                "offset": null
            }

        Example::

            >>> from trustedtwin.tt_api import TTRESTService
            >>> tt_client = TTRESTService(tt_auth="TT_SECRET")
            >>> status, text = tt_client.list_stickers()
            >>> status
            200 (int)
            >>> text
            {
                "stickers": "None"
            } (str)

        """
