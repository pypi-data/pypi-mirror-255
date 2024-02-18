# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spaces', 'spaces.zero']

package_data = \
{'': ['*']}

install_requires = \
['gradio',
 'httpx>=0.20',
 'psutil>=2,<6',
 'pydantic>=1,<3',
 'requests>=2.19,<3.0',
 'typing-extensions>=4,<5']

setup_kwargs = {
    'name': 'spaces',
    'version': '0.23.0',
    'description': 'Utilities for Hugging Face Spaces',
    'long_description': '# Hugging Face Spaces\n\n## Installation\n\n`pip install spaces`\n',
    'author': 'Charles Bensimon',
    'author_email': 'charles@huggingface.co',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://huggingface.co',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
