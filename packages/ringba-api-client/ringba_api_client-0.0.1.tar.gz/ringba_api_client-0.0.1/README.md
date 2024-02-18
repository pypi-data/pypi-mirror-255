
# Ringba API Client


<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)
[![Tests](https://github.com/nat5142/ringba-api-client/workflows/tests/badge.svg)](https://github.com/nat5142/ringba-api-client/actions?workflow=tests)
[![Codecov](https://codecov.io/gh/nat5142/ringba-api-client/branch/main/graph/badge.svg)](https://codecov.io/gh/nat5142/ringba-api-client)
[![Read the Docs](https://readthedocs.org/projects/ringba-api-client/badge/)](https://ringba-api-client.readthedocs.io/)
[![PyPI - License](https://img.shields.io/pypi/l/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


</div>


Simple Rrequest package to integrate with the Ringba Public API


* GitHub repo: <https://github.com/nat5142/ringba-api-client.git>
* Documentation: <https://ringba-api-client.readthedocs.io>
* Free software: MIT


## Quickstart

Install:

```shell
pip install ringba-api-client
```

Import:

```python
from ringba_api_client import RingbaApiClient
```

Initialize:

```python
ringba = RingbaApiClient(api_key='XXXXXXXXXXXXXXXX')
```

Use:

```python
target = ringba.get_targets(target_id='abdc12345')
```


## TODO:

- Add schema validation for create/update bodies


## Credits

This package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.

[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage
