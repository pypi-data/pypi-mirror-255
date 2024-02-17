# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cumulative', 'cumulative.transforms']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.7.1',
 'pandas>=1.5.3',
 'scikit-learn>=1.2.2',
 'scipy>=1.11.4',
 'statsmodels>=0.14.1',
 'tabulate>=0.9.0,<0.10.0',
 'tqdm>=4.66.1',
 'tsfel>=0.1.6']

setup_kwargs = {
    'name': 'cumulative',
    'version': '0.0.28',
    'description': 'Manipulation and analysis of data series collections',
    'long_description': '<p align="center">\n<img width="50%" height="50%" src="https://elehcimd.github.io/cumulative/assets/img/logo-black.svg" alt="CUMULATIVE Logo">\n</p>\n\n<p align="center">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/test.svg" alt="Test">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/coverage.svg" alt="Coverage">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/python.svg" alt="Python">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/pypi.svg" alt="PyPi">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/license.svg" alt="License">\n<img src="https://elehcimd.github.io/cumulative/assets/img/badges/code-style.svg" alt="Code style">\n</p>\n\n---\n\n**Cumulative** is an open source project and Python package that provides an intuitive in-memory interface to transform and analyse large collections of time series with composable pipelines.\n\n---\n\n* **Documentation**: [https://elehcimd.github.io/cumulative/](https://elehcimd.github.io/cumulative/)\n* **Source code**: [https://github.com/elehcimd/cumulative](https://github.com/elehcimd/cumulative)\n\n---\n\n## Key features\n\n* **Transformations**: Apply vectorized time series transformations as composable operations\n* **Interoperability**: Access the underlying data at any time as a Pandas data frame\n* **Flexibility**: Implement custom transformations and store arbitrary metadata\n\n## Requirements\n\n* **Python >=3.10**\n\n## Installation\n\n```\npip install cumulative\n```\n\n## License\n\nThis project is licensed under the terms of the [BSD 3-Clause License](https://elehcimd.github.io/cumulative/license/).\n\n\n',
    'author': 'Michele Dallachiesa',
    'author_email': 'michele.dallachiesa@sigforge.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://elehcimd.github.io/cumulative/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10.0',
}


setup(**setup_kwargs)
