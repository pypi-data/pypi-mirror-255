# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['video_vit']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'torch', 'zetascale']

entry_points = \
{'console_scripts': ['swarms = swarms.cli._cli:main']}

setup_kwargs = {
    'name': 'video-vit',
    'version': '0.0.1',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Video Vit\nOpen source implementation of a vision transformer that can understand Videos using max vit as a foundation.\n\n## Installation\n``\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/VideoVIT',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
