# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pragma',
 'pragma.core',
 'pragma.core.abis',
 'pragma.core.mixins',
 'pragma.core.randomness',
 'pragma.publisher',
 'pragma.publisher.fetchers',
 'pragma.publisher.future_fetchers']

package_data = \
{'': ['*']}

install_requires = \
['aioresponses>=0.7.4,<0.8.0',
 'cairo-lang>=0.12,<0.13',
 'deprecated>=1.2.14,<2.0.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'requests-mock>=1.11.0,<2.0.0',
 'starknet.py==0.19.0a0',
 'typer==0.6.1']

setup_kwargs = {
    'name': 'pragma-sdk',
    'version': '1.1.7',
    'description': 'Core package for rollup-native Pragma Oracle',
    'long_description': "# Pragma SDK\n\n[![codecov](https://codecov.io/gh/Astraly-Labs/pragma-sdk/graph/badge.svg?token=98pUFYGHIK)](https://codecov.io/gh/Astraly-Labs/pragma-sdk)\n\n[![Checks](https://github.com/Astraly-Labs/pragma-sdk/actions/workflows/checks.yml/badge.svg)](https://github.com/Astraly-Labs/pragma-sdk/actions/workflows/checks.yml)\n\n[![Package](https://img.shields.io/pypi/v/pragma-sdk)](https://pypi.org/project/pragma-sdk/)\n\n---\n\n**Pragma SDK, written in Python.**\n\nOne can leverage this SDK to interact with Pragma on Starknet.\nThis SDK should also be used by Data Providers willing to push data on Pragma contracts.\n\n## About\n\nFor more information, see the [project's repository](https://github.com/Astraly-Labs/Pragma), [documentation overview](https://docs.pragmaoracle.com/) and [documentation on how to publish data](https://docs.pragmaoracle.com/using-pragma/publishing-data).\n\n## Contributing\n\nSee the [CONTRIBUTING](./CONTRIBUTING.md) guide.",
    'author': '0xevolve',
    'author_email': 'matthias@pragma.build',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://pragma.build',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
