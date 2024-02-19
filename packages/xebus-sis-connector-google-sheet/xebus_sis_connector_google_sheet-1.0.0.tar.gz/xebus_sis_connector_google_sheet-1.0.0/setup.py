# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['majormode',
 'majormode.xebus',
 'majormode.xebus.sis',
 'majormode.xebus.sis.connector',
 'majormode.xebus.sis.connector.sis']

package_data = \
{'': ['*']}

install_requires = \
['gspread>=5.12,<6.0',
 'perseus-core-library>=1.19,<2.0',
 'perseus-getenv-library>=1.0,<2.0',
 'requests>=2.31,<3.0',
 'xebus-core-library>=1.4,<2.0',
 'xebus-sis-connector-core-library>=0.0,<0.1']

setup_kwargs = {
    'name': 'xebus-sis-connector-google-sheet',
    'version': '1.0.0',
    'description': "Connector to fetch data from a school's Eduka information system",
    'long_description': "# Xebus Google Sheet SIS Connector\nConnector to fetch family data from a school's Google Sheet document.\n",
    'author': 'Daniel CAUNE',
    'author_email': 'daniel.caune@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/xebus/xebus-sis-connector-google-sheet',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
