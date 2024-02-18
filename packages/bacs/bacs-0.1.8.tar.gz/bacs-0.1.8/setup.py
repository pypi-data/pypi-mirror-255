# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bacs']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0']

extras_require = \
{':python_version == "3.8"': ['scipy>=1.10.0,<1.11.0'],
 ':python_version >= "3.9"': ['scipy>=1.11.0']}

setup_kwargs = {
    'name': 'bacs',
    'version': '0.1.8',
    'description': 'Bundle Adjustment For Camera Systems',
    'long_description': '# BACS: Bundle Adjustment For Camera Systems\n\nThis is a Python implementation of BACS, a bundle adjustment for camera systems with points at infinity.\nIt was originally written in Matlab and published by Johannes Schneider, Falko Schindler, Thomas Läbe, and Wolfgang Förstner in 2012.\n\n## Usage\n\nRun\n\n```bash\npython3 -m pip install bacs\n```\n\nto install the library.\nHave a look at the [doc string](https://github.com/zauberzeug/bacs/blob/main/bacs/bacs.py#L47-L92) for explanation of the parameters.\n\n## Testing and development\n\nMake sure you have NumPy and SciPy installed:\n\n```bash\npython3 -m pip install numpy scipy\n```\n\nBy running the provided examples with\n\n```bash\npython3 main.py\n```\n\nyou can verify that BACS is working correctly (eg. there is no `git diff` in the results folder after execution).\n\n## Resources\n\nFurther explanation and visualization can be found on the [BACS project page](https://www.ipb.uni-bonn.de/data-software/bacs/), the corresponding [Matlab demo](https://www.ipb.uni-bonn.de/html/software/bacs/v0.1/demo-v0.1.html) as well as the original [publication](https://www.isprs-ann-photogramm-remote-sens-spatial-inf-sci.net/I-3/75/2012/isprsannals-I-3-75-2012.pdf).\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/zauberzeug/bacs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.13',
}


setup(**setup_kwargs)
