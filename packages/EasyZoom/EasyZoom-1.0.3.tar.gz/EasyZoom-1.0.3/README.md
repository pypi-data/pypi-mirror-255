# Python Zoom client

## what does this package do

- Authenticate Zooom Credentials
- Generate Zoom link

## Quick Start

```
$pip install EasyZoom
```

```
from easy_zoom.client import Client

client_instance = Client()
```

## Methods

1. `set_account_id(account_id: str)`
2. `set_client_id(client_id: str)`
3. `set_client_secret(client_secret: str)`
4. `authenticate()`
5. `set_date(date: str)`
6. `set_time(time: str)`
7. `set_topic(topic: str)`
8. `generate_link()`

## License

Usage is provided under the [MIT License](http://opensource.org/licenses/mit-license.php). See LICENSE for the full details.