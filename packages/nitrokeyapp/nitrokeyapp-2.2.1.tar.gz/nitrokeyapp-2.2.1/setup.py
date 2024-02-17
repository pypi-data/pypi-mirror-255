# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nitrokeyapp', 'nitrokeyapp.secrets_tab']

package_data = \
{'': ['*'], 'nitrokeyapp': ['ui/*', 'ui/LICENSES/*', 'ui/i18n/*', 'ui/icons/*']}

install_requires = \
['pySide6>=6.6.0',
 'pynitrokey==0.4.45',
 'pyudev>=0.24.1,<0.25.0',
 'qt_material>=2.14,<3.0']

extras_require = \
{':sys_platform == "win32"': ['pywin32==305']}

entry_points = \
{'console_scripts': ['nitrokeyapp = nitrokeyapp.__main__:main']}

setup_kwargs = {
    'name': 'nitrokeyapp',
    'version': '2.2.1',
    'description': 'Graphical application to manage Nitrokey devices',
    'long_description': '# Nitrokey App 2\n\nThis application allows to manage Nitrokey 3 devices. To manage Nitrokey Pro and Nitrokey Storage devices, use the older [Nitrokey App](https://github.com/Nitrokey/nitrokey-app).\n\n## Features\n\nThe following features are currently implemented.\n\n- Firmware update\n- Passwords\n    - TOTP\n    - HOTP\n\n## Download\n\nExecutable binaries for Linux and Windows as well as a MSI installer for Windows can be downloaded from the [releases](https://github.com/Nitrokey/nitrokey-app2/releases).\n\n### Compiling for Linux and macOS\n\nThis project uses [Poetry](https://python-poetry.org/) as its dependency management and packaging system.\nSee the [documentation](https://python-poetry.org/docs/) of *Poetry* for available commands.\n\nThe application can be compiled by executing:\n\n```\ngit clone https://github.com/Nitrokey/nitrokey-app2.git\ncd nitrokey-app2\nmake init\nmake build\npoetry shell\nnitrokeyapp\n```\n\n## Dependencies\n\n* [pynitrokey ](https://github.com/Nitrokey/pynitrokey)\n* Python >3.9\n\n## Author\n\nNitrokey GmbH, Jan Suhr and [contributors](https://github.com/Nitrokey/nitrokey-app2/graphs/contributors).\n',
    'author': 'Nitrokey',
    'author_email': 'pypi@nitrokey.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/nitrokey/nitrokey-app2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.13',
}


setup(**setup_kwargs)
