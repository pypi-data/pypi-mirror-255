
# Rest Wrapper


<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/rest-wrapper.svg)](https://pypi.python.org/pypi/rest-wrapper)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rest-wrapper.svg)](https://pypi.python.org/pypi/rest-wrapper)
[![Tests](https://github.com/nat5142/rest-wrapper/workflows/tests/badge.svg)](https://github.com/nat5142/rest-wrapper/actions?workflow=tests)
[![Codecov](https://codecov.io/gh/nat5142/rest-wrapper/branch/main/graph/badge.svg)](https://codecov.io/gh/nat5142/rest-wrapper)
[![Read the Docs](https://readthedocs.org/projects/rest-wrapper/badge/)](https://rest-wrapper.readthedocs.io/)
[![PyPI - License](https://img.shields.io/pypi/l/rest-wrapper.svg)](https://pypi.python.org/pypi/rest-wrapper)

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


</div>


Simple, extendable base rest client for python. I've rewritten this pattern time after time, figured I would just package it and install when necessary.


* GitHub repo: <https://github.com/nat5142/rest-wrapper.git>
* Documentation: <https://rest-wrapper.readthedocs.io>
* Free software: MIT


## Features

Rest Wrapper provides a simple exposure of the `requests` module. Just provide a `base_url` to target and go from there:

```python
from rest_wrapper import RestClient

client = RestClient('https://example.com/')

# make a GET request. just provide an endpoint to append it to your base_url
resp = client.get('users/1/info')

# POST request
resp = client.post('users', json={'name': 'nick', 'username': 'nat5142'})  # kwargs are passed directly to the request itself

# don't append, just request any full URL:
resp = client.get('https://www.google.com/search?q=cats', append_url=False)
```

Or, use the client to make constructing your own API Wrappers easier:

```python
import os
from rest_wrapper import RestClient


class SomeApiWrapper(RestClient):
    base_url = 'https://some-api.com/'

    def authenticate(self):
        # authenticate method is invoked at the end of the object intialization.
        self.session.headers.update({
            'X-Api-Key': os.environ['API_KEY']
        })


client = SomeApiWrapper()

resp = client.get('/api/v1/users')  # will request https://some-api.com/api/v1/users
```

## Credits

This package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.

[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage
