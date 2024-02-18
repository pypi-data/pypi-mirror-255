# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crypto_com']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3,<4', 'websockets>=12,<13']

setup_kwargs = {
    'name': 'crypto-com-client',
    'version': '1.2',
    'description': 'Crypto.com websocket api client',
    'long_description': 'Crypto.com websocket api client\n=================================\n[![Build Status](https://travis-ci.com/maxpowel/crypto_com_client.svg?branch=master)](https://travis-ci.com/maxpowel/crypto_com_client)\n[![Maintainability](https://api.codeclimate.com/v1/badges/9c2c51fed72ca3aeacf6/maintainability)](https://codeclimate.com/github/maxpowel/crypto_com_client/maintainability)\n[![Test Coverage](https://api.codeclimate.com/v1/badges/9c2c51fed72ca3aeacf6/test_coverage)](https://codeclimate.com/github/maxpowel/crypto_com_client/test_coverage)\n\n\nThis is a low level api client, it just connects the exchange api with your python code in the most simple way. Over\nthis library, you can build your awesome applications or high level api.\nFor more information, check the [library documentation](https://maxpowel.github.io/crypto_com_client/), the [official documentation](https://exchange-docs.crypto.com/) and the `examples` directory.\n\nFeatures\n--------\nThis library is optimized to be small, fast and secure. \n  * Fully tested: 100% code coverage\n  * Simple: It just does one thing, but it does it right\n  * Fast: Relies on asyncio so latency and memory usage is near zero (much better than threading or multiprocessing)\n  * No forced dependencies: Just `websockets` and `orjson`. No super modern cool features that you probably don\'t want\n\n\nGetting started\n---------------\nThere are two kinds of `apis`, the `user` and `market`. \nThe `user` type requires providing api credentials (access and secret key)\n\nBefore using the library, you have to install it:\n```bash\npip install crypto_com_client\n```\n\nThe most simple example, subscribing to an `orderbook`:\n\n```python\nfrom crypto_com.crypto_com import MarketClient\nimport asyncio\nimport logging\n\nlogging.basicConfig(level=logging.INFO)\n\nasync def run():\n    async with MarketClient() as client:\n        await client.subscribe(["book.CRO_USDC.10"])\n        while True:\n            event = await client.next_event()\n            print(event)\n\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(run())\n```\n\nIf you want to use the `user` api first get you api `key` and `secret`.\n\n```python\nfrom crypto_com import UserClient\nimport asyncio\nimport os\nimport logging\n\nlogging.basicConfig(level=logging.INFO)\n\nasync def run():\n    async with UserClient(\n            api_key=os.environ["API_KEY"],\n            api_secret=os.environ["API_SECRET"]\n    ) as client:\n        await client.send(\n            client.build_message(\n                method="private/get-open-orders",\n                params={\n                    "instrument_name": "CRO_USDC",\n                    "page_size": 10,\n                    "page": 0\n                }\n            )\n        )\n        event = await client.next_event()\n        print(event)\n\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(run())\n\n```\n\nWith these two examples you can use the whole api. Just check the API documentation to know the different methods\nand parameters.\n\nContributing\n============\nIf you have any suggestion, detect any bug or want any feature, please open an `issue` so we can discuss it.\n\n\nTests\n=====\nTo run the tests just run `tox`\n\nIt will run in first instance `flake8`, then `pylint` and finally `pytest` with code coverage check.\nThe only rule ignored is `max-line-length=120` basically because nowadays monitors are big enough for this.\nWebsockets import has E0611 disabled because pylint does not process `__all__` correctly',
    'author': 'Alvaro Garcia',
    'author_email': 'maxpowel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/maxpowel/crypto_com_client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
