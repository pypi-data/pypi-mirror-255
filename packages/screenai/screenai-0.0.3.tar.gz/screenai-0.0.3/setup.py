# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['screenai']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'swarms', 'torch', 'torchvision', 'zetascale']

setup_kwargs = {
    'name': 'screenai',
    'version': '0.0.3',
    'description': 'Screen AI - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Screen AI\nImplementation of the ScreenAI model from the paper: "A Vision-Language Model for UI and Infographics Understanding"\n\n## Install\n`pip3 install screenai`\n\n## Usage\n```python\n\n\n```\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/ScreenAI',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
