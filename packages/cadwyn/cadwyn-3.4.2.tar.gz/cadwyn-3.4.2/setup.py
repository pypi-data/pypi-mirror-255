# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cadwyn', 'cadwyn.codegen', 'cadwyn.codegen._plugins', 'cadwyn.structure']

package_data = \
{'': ['*']}

install_requires = \
['better-ast-comments>=1.2.1,<1.3.0',
 'fastapi>=0.96.1',
 'pydantic>=1.0.0',
 'typing-extensions',
 'verselect>=0.0.6']

extras_require = \
{'cli': ['typer>=0.7.0']}

entry_points = \
{'console_scripts': ['cadwyn = cadwyn.__main__:app']}

setup_kwargs = {
    'name': 'cadwyn',
    'version': '3.4.2',
    'description': 'Production-ready community-driven modern Stripe-like API versioning in FastAPI',
    'long_description': '# Cadwyn\n\nProduction-ready community-driven modern [Stripe-like](https://stripe.com/blog/api-versioning) API versioning in FastAPI\n\n---\n\n<p align="center">\n<a href="https://github.com/zmievsa/cadwyn/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/zmievsa/cadwyn/actions/workflows/test.yaml/badge.svg?branch=main&event=push" alt="Test">\n</a>\n<a href="https://codecov.io/gh/ovsyanka83/cadwyn" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/ovsyanka83/cadwyn?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/cadwyn/" target="_blank">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/cadwyn?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/cadwyn/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/cadwyn?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n## Who is this for?\n\nCadwyn allows you to support a single version of your code while auto-generating the schemas and routes for older versions. You keep API versioning encapsulated in small and independent "version change" modules while your business logic stays simple and knows nothing about versioning.\n\nIts [approach](https://docs.cadwyn.dev/theory/#ii-migration-based-response-building) will be useful if you want to:\n\n1. Support many API versions for a long time\n2. Effortlessly backport features and bugfixes to older API versions\n\nWhether you are a newbie in API versioning, a pro looking for a sophisticated tool, an experimenter looking to build a similar framework, or even someone who just wants to learn about all approaches to API versioning -- Cadwyn has the functionality, theory, and documentation to cover all the mentioned use cases.\n\n## Get started\n\nThe [documentation](https://docs.cadwyn.dev) has everything you need to succeed.\n\n## Sponsors\n\nThese are our gorgeous sponsors. They are using Cadwyn and are sponsoring it through various means. Contact [me](https://github.com/zmievsa) if you would like to become one too!\n\n[![Monite](https://docs.cadwyn.dev/img/sponsor_logos/monite.png)](https://docs.monite.com/)\n',
    'author': 'Stanislav Zmiev',
    'author_email': 'zmievsa@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/zmievsa/cadwyn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
