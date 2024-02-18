# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starknet_py',
 'starknet_py.abi',
 'starknet_py.abi.v1',
 'starknet_py.abi.v2',
 'starknet_py.cairo',
 'starknet_py.cairo.deprecated_parse',
 'starknet_py.cairo.v1',
 'starknet_py.cairo.v2',
 'starknet_py.hash',
 'starknet_py.net',
 'starknet_py.net.account',
 'starknet_py.net.models',
 'starknet_py.net.schemas',
 'starknet_py.net.signer',
 'starknet_py.net.udc_deployer',
 'starknet_py.proxy',
 'starknet_py.serialization',
 'starknet_py.serialization.data_serializers',
 'starknet_py.utils',
 'starknet_py.utils.sync']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0',
 'asgiref>=3.4.1,<4.0.0',
 'crypto-cpp-py>=1.4.0,<2.0.0',
 'lark>=1.1.5,<2.0.0',
 'marshmallow-dataclass<8.7.0',
 'marshmallow-oneofschema>=3.0.1,<4.0.0',
 'marshmallow>=3.15.0,<4.0.0',
 'poseidon-py>=0.1.3,<0.2.0',
 'pycryptodome>=3.17,<4.0',
 'typing-extensions>=4.3.0,<5.0.0']

extras_require = \
{'docs': ['sphinx>=4.3.1,<8.0.0',
          'enum-tools[sphinx]==0.11.0',
          'furo>=2023.5.20,<2024.0.0']}

setup_kwargs = {
    'name': 'starknet-py',
    'version': '0.19.0',
    'description': 'A python SDK for Starknet',
    'long_description': '<div align="center">\n    <img src="https://raw.githubusercontent.com/software-mansion/starknet.py/master/graphic.png" alt="starknet.py"/>\n</div>\n<h2 align="center">Starknet SDK for Python</h2>\n\n<div align="center">\n\n[![codecov](https://codecov.io/gh/software-mansion/starknet.py/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet.py)\n[![pypi](https://img.shields.io/pypi/v/starknet.py)](https://pypi.org/project/starknet.py/)\n[![build](https://img.shields.io/github/actions/workflow/status/software-mansion/starknet.py/checks.yml)](https://github.com/software-mansion/starknet.py/actions)\n[![docs](https://readthedocs.org/projects/starknetpy/badge/?version=latest)](https://starknetpy.readthedocs.io/en/latest/?badge=latest)\n[![license](https://img.shields.io/badge/license-MIT-black)](https://github.com/software-mansion/starknet.py/blob/master/LICENSE.txt)\n[![stars](https://img.shields.io/github/stars/software-mansion/starknet.py?color=yellow)](https://github.com/software-mansion/starknet.py/stargazers)\n[![starkware](https://img.shields.io/badge/powered_by-StarkWare-navy)](https://starkware.co)\n\n</div>\n\n## 📘 Documentation\n\n- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)\n- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)\n- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)\n- [API](https://starknetpy.rtfd.io/en/latest/api.html)\n- [Migration guide](https://starknetpy.readthedocs.io/en/latest/migration_guide.html)\n\n## ⚙️ Installation\n\nInstallation varies between operating systems.\n\n[See our documentation on complete instructions](https://starknetpy.rtfd.io/en/latest/installation.html)\n\n## ▶️ Example usage\n\n### Asynchronous API\n\nThis is the recommended way of using the SDK.\n\n```python\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.full_node_client import FullNodeClient\n\ncontract = await Contract.from_address(\n    address="0x06689f1bf69af5b8e94e5ab9778c885b37c593d1156234eb423967621f596e73",\n    client=FullNodeClient(node_url="https://your.node.url"),\n)\n(value,) = await contract.functions["get_balance"].call()\n```\n\n### Synchronous API\n\nYou can access synchronous world with `_sync` postfix.\n\n```python\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.full_node_client import FullNodeClient\n\ncontract = Contract.from_address_sync(\n    address="0x06689f1bf69af5b8e94e5ab9778c885b37c593d1156234eb423967621f596e73",\n    client=FullNodeClient(node_url="https://your.node.url"),\n)\n(value,) = contract.functions["get_balance"].call_sync()\n```\n\nFor more examples click [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).\n',
    'author': 'Tomasz Rejowski',
    'author_email': 'tomasz.rejowski@swmansion.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/software-mansion/starknet.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
