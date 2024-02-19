# peliqan

A python client that allows any script to connect to a Peliqan environment.

# Install

```bash
$ pip install peliqan
```

# Usage

## Make a connection
```python
from peliqan import Peliqan

jwt = "MY_JWT_TOKEN"
backend_url="MY_PELIQAN_URL"

pq = Peliqan(jwt, backend_url) 
```

### Argument List
The **`Peliqan`** class takes two arguments:

- **jwt** (*required*): This is the JWT token provided to you and is used to authenticate requests from the client to the server. 


- **backend_url** (*optional*): This is the `instance_url` that points to a specific Peliqan environment. 
If no value is provided, the client will look for the `PELIQAN_URL` environment variable. If it is not set, 
then the value defaults to *https://app.eu.peliqan.io/*.

Learn how to find your Peliqan environment and JWT token [here](https://peliqan.notion.site/Peliqan-API-ab7e96d5122d427b877fd488ea812966/).

### Environment Variables
Currently, only one environment variable is available.

- **PELIQAN_UR**: If this variable is set then we need not provide a backend_url, while instantiating the client.
- 
## Documentation
See [here](https://peliqan.notion.site/Building-data-apps-bfd91569d0824629b090dc439d39ca63/) 
to learn more about building data apps.

See [here](https://peliqan.notion.site/Peliqan-documentation-52f91ae8f3364157a7a7fe063c9f694d/) 
to learn more about [Peliqan.io](https://www.peliqan.io/).

