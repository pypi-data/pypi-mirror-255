# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['audio_flamingo']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'swarms', 'torchaudio', 'zetascale']

setup_kwargs = {
    'name': 'audio-flamingo',
    'version': '0.0.3',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# AudioFlamingo\nImplementation of the model "AudioFlamingo" from the paper: "Audio Flamingo: A Novel Audio Language Model with Few-Shot Learning and Dialogue Abilities". [PAPER LINK](https://arxiv.org/pdf/2402.01831.pdf)\n\n\n## Install\n`pip3 install audio-flamingo`\n\n## Usage\n```python\nimport torch\nfrom audio_flamingo.model import AudioFlamingo\n\n# Generate a random input sequence\ntext = torch.randint(0, 256, (1, 1024))\naudio = torch.randn(1, 16000)\n\n# Initialize AudioFlamingo model\nmodel = AudioFlamingo(\n    dim=512,\n    num_tokens=256,\n    max_seq_len=1024,\n    heads=8,\n    depth=6,\n    dim_head=64,\n    dropout=0.1,\n    context_dim=512,\n)\n\n# Pass the input sequence through the model\noutput = model(text, audio)  # (1, 1024, 256)\n\n# Print the output shape\nprint(output.shape)\n# Path: audio_flamingo/model.py\n\n```\n\n# License\nMIT\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/AudioFlamingo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
