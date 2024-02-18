# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ringba_api_client']

package_data = \
{'': ['*']}

install_requires = \
['rest-wrapper==0.0.2']

setup_kwargs = {
    'name': 'ringba-api-client',
    'version': '0.0.1',
    'description': 'Simple Rrequest package to integrate with the Ringba Public API',
    'long_description': '\n# Ringba API Client\n\n\n<div align="center">\n\n[![PyPI - Version](https://img.shields.io/pypi/v/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)\n[![Tests](https://github.com/nat5142/ringba-api-client/workflows/tests/badge.svg)](https://github.com/nat5142/ringba-api-client/actions?workflow=tests)\n[![Codecov](https://codecov.io/gh/nat5142/ringba-api-client/branch/main/graph/badge.svg)](https://codecov.io/gh/nat5142/ringba-api-client)\n[![Read the Docs](https://readthedocs.org/projects/ringba-api-client/badge/)](https://ringba-api-client.readthedocs.io/)\n[![PyPI - License](https://img.shields.io/pypi/l/ringba-api-client.svg)](https://pypi.python.org/pypi/ringba-api-client)\n\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n\n</div>\n\n\nSimple Rrequest package to integrate with the Ringba Public API\n\n\n* GitHub repo: <https://github.com/nat5142/ringba-api-client.git>\n* Documentation: <https://ringba-api-client.readthedocs.io>\n* Free software: MIT\n\n\n## Quickstart\n\nInstall:\n\n```shell\npip install ringba-api-client\n```\n\nImport:\n\n```python\nfrom ringba_api_client import RingbaApiClient\n```\n\nInitialize:\n\n```python\nringba = RingbaApiClient(api_key=\'XXXXXXXXXXXXXXXX\')\n```\n\nUse:\n\n```python\ntarget = ringba.get_targets(target_id=\'abdc12345\')\n```\n\n\n## TODO:\n\n- Add schema validation for create/update bodies\n\n\n## Credits\n\nThis package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.\n\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage\n',
    'author': 'Nick Tulli',
    'author_email': 'ntulli.dev@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/nat5142/ringba-api-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
