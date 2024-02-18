# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['momento',
 'momento.auth',
 'momento.common_data',
 'momento.common_data.vector_index',
 'momento.config',
 'momento.config.transport',
 'momento.errors',
 'momento.internal',
 'momento.internal._utilities',
 'momento.internal.aio',
 'momento.internal.synchronous',
 'momento.requests',
 'momento.requests.vector_index',
 'momento.responses',
 'momento.responses.control',
 'momento.responses.control.cache',
 'momento.responses.control.signing_key',
 'momento.responses.data',
 'momento.responses.data.dictionary',
 'momento.responses.data.list',
 'momento.responses.data.scalar',
 'momento.responses.data.set',
 'momento.responses.data.sorted_set',
 'momento.responses.pubsub',
 'momento.responses.vector_index',
 'momento.responses.vector_index.control',
 'momento.responses.vector_index.data',
 'momento.retry',
 'momento.utilities']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.46.0,<2.0.0',
 'momento-wire-types>=0.105.3,<0.106.0',
 'pyjwt>=2.4.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4']}

setup_kwargs = {
    'name': 'momento',
    'version': '1.18.0',
    'description': 'SDK for Momento',
    'long_description': '<head>\n  <meta name="Momento Python Client Library Documentation" content="Python client software development kit for Momento Cache">\n</head>\n<img src="https://docs.momentohq.com/img/momento-logo-forest.svg" alt="logo" width="400"/>\n\n[![project status](https://momentohq.github.io/standards-and-practices/badges/project-status-official.svg)](https://github.com/momentohq/standards-and-practices/blob/main/docs/momento-on-github.md)\n[![project stability](https://momentohq.github.io/standards-and-practices/badges/project-stability-stable.svg)](https://github.com/momentohq/standards-and-practices/blob/main/docs/momento-on-github.md)\n\n# Momento Python Client Library\n\nMomento Cache is a fast, simple, pay-as-you-go caching solution without any of the operational overhead\nrequired by traditional caching solutions.  This repo contains the source code for the Momento Python client library.\n\nTo get started with Momento you will need a Momento Auth Token. You can get one from the [Momento Console](https://console.gomomento.com).\n\n* Website: [https://www.gomomento.com/](https://www.gomomento.com/)\n* Momento Documentation: [https://docs.momentohq.com/](https://docs.momentohq.com/)\n* Getting Started: [https://docs.momentohq.com/getting-started](https://docs.momentohq.com/getting-started)\n* Python SDK Documentation: [https://docs.momentohq.com/develop/sdks/python](https://docs.momentohq.com/develop/sdks/python)\n* Discuss: [Momento Discord](https://discord.gg/3HkAKjUZGq)\n\n## Packages\n\nThe Momento Python SDK package is available on pypi: [momento](https://pypi.org/project/momento/).\n\n## Usage\n\nThe examples below require an environment variable named `MOMENTO_API_KEY` which must\nbe set to a valid Momento API key. You can get one from the [Momento Console](https://console.gomomento.com).\n\nPython 3.10 introduced the `match` statement, which allows for [structural pattern matching on objects](https://peps.python.org/pep-0636/#adding-a-ui-matching-objects).\nIf you are running python 3.10 or greater, here is a quickstart you can use in your own project:\n\n```python\nfrom datetime import timedelta\n\nfrom momento import CacheClient, Configurations, CredentialProvider\nfrom momento.responses import CacheGet\n\ncache_client = CacheClient(\n    Configurations.Laptop.v1(), CredentialProvider.from_environment_variable("MOMENTO_API_KEY"), timedelta(seconds=60)\n)\n\ncache_client.create_cache("cache")\ncache_client.set("cache", "my-key", "my-value")\nget_response = cache_client.get("cache", "my-key")\nmatch get_response:\n    case CacheGet.Hit() as hit:\n        print(f"Got value: {hit.value_string}")\n    case _:\n        print(f"Response was not a hit: {get_response}")\n\n```\n\nThe above code uses [structural pattern matching](https://peps.python.org/pep-0636/), a feature introduced in Python 3.10.\nUsing a Python version less than 3.10? No problem. Here is the same example compatible across all versions of Python:\n\n```python\nfrom datetime import timedelta\n\nfrom momento import CacheClient, Configurations, CredentialProvider\nfrom momento.responses import CacheGet\n\ncache_client = CacheClient(\n    configuration=Configurations.Laptop.v1(),\n    credential_provider=CredentialProvider.from_environment_variable("MOMENTO_API_KEY"),\n    default_ttl=timedelta(seconds=60),\n)\ncache_client.create_cache("cache")\ncache_client.set("cache", "myKey", "myValue")\nget_response = cache_client.get("cache", "myKey")\nif isinstance(get_response, CacheGet.Hit):\n    print(f"Got value: {get_response.value_string}")\n\n```\n\n## Getting Started and Documentation\n\nDocumentation is available on the [Momento Docs website](https://docs.momentohq.com).\n\n## Examples\n\nWorking example projects, with all required build configuration files, are available for both Python 3.10 and up\nand Python versions before 3.10:\n\n* [Python 3.10+ examples](./examples/py310)\n* [Pre-3.10 Python examples](./examples/prepy310)\n\n## Developing\n\nIf you are interested in contributing to the SDK, please see the [CONTRIBUTING](./CONTRIBUTING.md) docs.\n\n----------------------------------------------------------------------------------------\nFor more info, visit our website at [https://gomomento.com](https://gomomento.com)!\n',
    'author': 'Momento',
    'author_email': 'hello@momentohq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gomomento.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
