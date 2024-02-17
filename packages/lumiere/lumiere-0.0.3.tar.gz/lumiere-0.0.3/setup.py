# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lumiere']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'swarms', 'torch', 'zetascale']

setup_kwargs = {
    'name': 'lumiere',
    'version': '0.0.3',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Lumiere \nImplementation of the text to video model LUMIERE from the paper: "A Space-Time Diffusion Model for Video Generation" by Google Research. I will mostly be implementing the modules from the diagram a and b in figure 4\n\n## Install\n`pip install lumiere`\n\n\n## Usage\n```\n\n```\n\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/LUMIERE',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
