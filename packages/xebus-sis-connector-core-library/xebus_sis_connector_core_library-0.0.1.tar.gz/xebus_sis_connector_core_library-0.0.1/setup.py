# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['majormode',
 'majormode.xebus',
 'majormode.xebus.sis',
 'majormode.xebus.sis.connector',
 'majormode.xebus.sis.connector.constant',
 'majormode.xebus.sis.connector.model']

package_data = \
{'': ['*']}

install_requires = \
['perseus-core-library>=1.19,<2.0', 'xebus-core-library>=1.4,<2.0']

setup_kwargs = {
    'name': 'xebus-sis-connector-core-library',
    'version': '0.0.1',
    'description': 'Xebus SIS Connector Core Python Library',
    'long_description': '# Xebus SIS Connector Core Python Library\nReusable Python components to develop a SIS connector\n',
    'author': 'Daniel CAUNE',
    'author_email': 'daniel.caune@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/xebus/xebus-sis-connector-core-python-library',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
