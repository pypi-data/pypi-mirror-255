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
    'version': '0.0.4',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Lumiere \nImplementation of the text to video model LUMIERE from the paper: "A Space-Time Diffusion Model for Video Generation" by Google Research. I will mostly be implementing the modules from the diagram a and b in figure 4\n\n## Install\n`pip install lumiere`\n\n\n## Usage\n```python\nimport torch\nfrom lumiere.model import AttentionBasedInflationBlock\n\n# B, T, H, W, D\nx = torch.randn(1, 4, 224, 224, 512)\n\n# Model\nmodel = AttentionBasedInflationBlock(dim=512, heads=4, dropout=0.1)\n\n# Forward pass\nout = model(x)\n\n# print\nprint(out.shape)  # Expected shape: [1, 4, 224, 224, 3]\n\n```\n\n\n# License\nMIT\n',
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
