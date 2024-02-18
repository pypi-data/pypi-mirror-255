# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['httpx_negotiate_sspi']

package_data = \
{'': ['*']}

install_requires = \
['httpx>0.16,<0.27', 'pywin32>=223']

setup_kwargs = {
    'name': 'httpx-negotiate-sspi',
    'version': '0.26.1a1',
    'description': 'SSPI authentication for httpx',
    'long_description': "# httpx-negotiate-sspi\n\n[![image](https://badge.fury.io/py/httpx-negotiate-sspi.svg)](https://badge.fury.io/py/httpx-negotiate-sspi)\n\nThis is a port of\n[requests-negotiate-sspi](https://github.com/brandond/requests-negotiate-sspi)\nfor [httpx](https://github.com/encode/httpx).\n\nThe implmentation stays close to the original, in an attempt to make any fixes\nor updates more straighforward.\n\nThe following is taken from the README of the original package with changes to\nreflect httpx.\n\n---\n\nAn implementation of HTTP Negotiate authentication for Requests. This\nmodule provides single-sign-on using Kerberos or NTLM using the Windows\nSSPI interface.\n\nThis module supports Extended Protection for Authentication (aka Channel\nBinding Hash), which makes it usable for services that require it,\nincluding Active Directory Federation Services.\n\n## Usage\n\n```python\nimport httpx\nfrom httpx_negotiate_sspi import HttpSspiAuth\n\nr = httpx.get('https://iis.contoso.com', auth=HttpSspiAuth())\n```\n\n## Options\n\n  - `username`: Username.  \n    Default: None\n\n  - `password`: Password.  \n    Default: None\n\n  - `domain`: NT Domain name.  \n    Default: '.' for local account.\n\n  - `service`: Kerberos Service type for remote Service Principal\n    Name.  \n    Default: 'HTTP'\n\n  - `host`: Host name for Service Principal Name.  \n    Default: Extracted from request URI\n\n  - `delegate`: Indicates that the user's credentials are to be delegated to the server.\n    Default: False\n\n\nIf username and password are not specified, the user's default\ncredentials are used. This allows for single-sign-on to domain resources\nif the user is currently logged on with a domain account.",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/rob-blackbourn/httpx-negotiate-sspi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
