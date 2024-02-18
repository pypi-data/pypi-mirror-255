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
    'version': '0.0.1',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# AudioFlamingo\nImplementation of the model "AudioFlamingo" from the paper: "Audio Flamingo: A Novel Audio Language Model with Few-Shot Learning and Dialogue Abilities"\n\n\n\n# License\nMIT\n',
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
