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
    'version': '0.0.4',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Video Vit\nOpen source implementation of a vision transformer that can understand Videos using max vit as a foundation. This uses max vit as the backbone vit and then packs the video tensor into a 4d tensor which is the input to the maxvit model. Implementing this because the new McVit came out and I need more practice. This is fully ready to train and I believe would perform amazingly.\n\n## Installation\n`$ pip install video-vit`\n\n## Usage\n```python\nimport torch\nfrom video_vit.main import VideoViT\n\n# Instantiate the VideoViT model with the specified parameters\nmodel = VideoViT(\n    num_classes=10,                 # Number of output classes\n    dim=64,                         # Dimension of the token embeddings\n    depth=(2, 2, 2),                # Depth of each stage in the model\n    dim_head=32,                    # Dimension of the attention head\n    window_size=7,                  # Size of the attention window\n    mbconv_expansion_rate=4,        # Expansion rate of the Mobile Inverted Bottleneck block\n    mbconv_shrinkage_rate=0.25,     # Shrinkage rate of the Mobile Inverted Bottleneck block\n    dropout=0.1,                    # Dropout rate\n    channels=3,                     # Number of input channels\n)\n\n# Create a random tensor with shape (batch_size, channels, frames, height, width)\nx = torch.randn(1, 3, 10, 224, 224)\n\n# Perform a forward pass through the model\noutput = model(x)\n\n# Print the shape of the output tensor\nprint(output.shape)\n\n\n```\n\n\n# License\nMIT\n',
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
