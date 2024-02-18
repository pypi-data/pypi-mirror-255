# infisical_api
infisical_api is a python client for the infisical REST API. I found some of the dependencies int he infisical_python client incompatible with some of my applications so I build this very simple version that utilizes the REST API.

Get Secret
```python
from infisical_api import infisical_api

secrets = infisical_api(service_token=token,infisical_url=url) # infisical_url is only needed if using self-hosted
username = secrets.get_secret(secret_name="USERNAME", path="/MYSQL").secretValue # path defaults to "/" when not specified
```