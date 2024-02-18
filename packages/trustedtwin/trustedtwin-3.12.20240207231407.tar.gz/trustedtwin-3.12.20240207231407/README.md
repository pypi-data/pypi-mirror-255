TrustedTwin Python Client (external info)
===

The Trusted Twin Python library makes it easy to use the Trusted Twin user infrastructure API in Python applications. 
The library version is consistent with the Swagger version of the Trusted Twin API.

Client offers synchronous and asynchronous versions which can be used for communication with TT API.

Requirements
---
Library requires Python3.6+.

Installation
--

For synchronous API client:
```shell
pip install trustedtwin
```

To use asynchronous client:
```shell
pip install trustedtwin[async]
```

By default, additional packages required by `asynchronous` version are not installed. 

Usage
---

### Authorization

For synchronous client:
```python
from trustedtwin.tt_api import TTRESTService

TT_SERVICE = TTRESTService(auth=$USER_SECRET)
```

For asynchronous client:
```python
from trustedtwin.tt_api_async import TTAsyncRESTService

TT_SERVICE = TTAsyncRESTService(auth=$USER_SECRET)
```

### Example calls

For synchronous client:
```python
import json 
from trustedtwin.tt_api import TTRESTService

status, response = TTRESTService().create_user_secret($ACCOUNT_UUID, $PIN)
resp = json.loads(response)

TT_SERVICE = TTRESTService(tt_auth=resp['secret'])

_body = {
    'description': {
        'custom_name': 'custom_value'
    }
}

status, response = TT_SERVICE.create_twin(body=_body)
resp = json.loads(response)
```

For asynchronous client:
```python
import json 
from trustedtwin.tt_api_async import TTAsyncRESTService

status, response = await TTAsyncRESTService().create_user_secret($ACCOUNT_UUID, $PIN)
resp = json.loads(response)

TT_SERVICE = TTAsyncRESTService(tt_auth=resp['secret'])

_body = {
    'description': {
        'custom_name': 'custom_value'
    }
}

status, response = await TT_SERVICE.create_twin(body=_body)
resp = json.loads(response)
```

For more information please navigate to the official [documentation](https://trustedtwin.com/docs/libraries/library-python.html).

TrustedTwin Python Client (internal info)
===

Updating the library
---

To update the Python library to the newest version:

1. Upload a tt_api.yaml file corresponding with the respective API version.
2. In the Gitlab interface in the left-hand side pane, select *Build* and go to the *Pipeline schedules* section.
3. By the *Deploy to official pyPi repository* schedule, click on the *Run pipeline schedule* button.
