# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tapisservice',
 'tapisservice.tapisdjango',
 'tapisservice.tapisfastapi',
 'tapisservice.tapisflask']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.6.0', 'tapipy>=1.6.0']

setup_kwargs = {
    'name': 'tapisservice',
    'version': '1.6.0',
    'description': "Python lib for interacting with an instance of the Tapis API Framework's tapisservice plugin.",
    'long_description': 'Tapipy plugin granting Tapis service functionality using `import tapisservice`.\n\n\n## Automated Builds with Make and Poetry\nThis repository includes a Makefile to automate tasks such as building the images and running tests.\nIt depends on Poetry; see the docs for installing on your platform: https://python-poetry.org/docs/\n\nNote: On Ubunut 20 LTS (and maybe other platforms?) you might hit an issue trying to run the `poetry build` \ncommand with your version of virtualenv; see this issue: https://github.com/python-poetry/poetry/issues/2972\n\nThe workaround, as described in the issue, is to remove the version of virtualenv bundled with Ubuntu and install\nit with pip:\n\n```\n $ sudo apt remove --purge python3-virtualenv virtualenv\n $ sudo apt install python3-pip   # if necessary \n $ pip3 install -U virtualenv\n```\n\n## Running the Tests\n\nIn order to run the tests, you will need to populate the `config-dev-develop.json` file within the `tests` with the service password for `abaco` in develop. If you do not know how to get that password, ask for help on the tacc-cloud slack team.\n\n',
    'author': 'Joe Stubbs',
    'author_email': 'jstubbs@tacc.utexas.edu',
    'maintainer': 'Joe Stubbs',
    'maintainer_email': 'jstubbs@tacc.utexas.edu',
    'url': 'https://github.com/tapis-project/tapipy-tapisservice',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
