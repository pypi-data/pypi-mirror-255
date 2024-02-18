# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src',
 'openapi_fal_rest': 'openapi-fal-rest/openapi_fal_rest',
 'openapi_fal_rest.api': 'openapi-fal-rest/openapi_fal_rest/api',
 'openapi_fal_rest.api.applications': 'openapi-fal-rest/openapi_fal_rest/api/applications',
 'openapi_fal_rest.api.billing': 'openapi-fal-rest/openapi_fal_rest/api/billing',
 'openapi_fal_rest.api.files': 'openapi-fal-rest/openapi_fal_rest/api/files',
 'openapi_fal_rest.models': 'openapi-fal-rest/openapi_fal_rest/models'}

packages = \
['fal',
 'fal.auth',
 'fal.console',
 'fal.exceptions',
 'fal.logging',
 'fal.toolkit',
 'fal.toolkit.file',
 'fal.toolkit.file.providers',
 'fal.toolkit.image',
 'fal.toolkit.utils',
 'openapi_fal_rest',
 'openapi_fal_rest.api',
 'openapi_fal_rest.api.applications',
 'openapi_fal_rest.api.billing',
 'openapi_fal_rest.api.files',
 'openapi_fal_rest.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.3.0',
 'auth0-python>=4.1.0,<5.0.0',
 'boto3>=1.33.8,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'colorama>=0.4.6,<0.5.0',
 'datadog-api-client==2.12.0',
 'dill==0.3.7',
 'fastapi==0.99.1',
 'grpc-interceptor>=0.15.0,<0.16.0',
 'grpcio>=1.50.0,<2.0.0',
 'httpx>=0.15.4,<0.25.0',
 'isolate-proto>=0.3.1,<0.4.0',
 'isolate[build]>=0.12.3,<1.0',
 'msgpack>=1.0.7,<2.0.0',
 'opentelemetry-api>=1.15.0,<2.0.0',
 'opentelemetry-sdk>=1.15.0,<2.0.0',
 'packaging>=21.3',
 'pathspec>=0.11.1,<0.12.0',
 'pillow>=10.2.0,<11.0.0',
 'portalocker>=2.7.0,<3.0.0',
 'pydantic<2.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=13.3.2,<14.0.0',
 'structlog>=22.3.0,<23.0.0',
 'types-python-dateutil>=2.8.0,<3.0.0',
 'typing-extensions>=4.7.1,<5.0.0',
 'websockets>=12.0,<13.0']

extras_require = \
{':python_version < "3.10"': ['importlib-metadata>=4.4']}

entry_points = \
{'console_scripts': ['fal = fal.cli:cli', 'fal-serverless = fal.cli:cli']}

setup_kwargs = {
    'name': 'fal',
    'version': '0.12.2',
    'description': 'fal is an easy-to-use Serverless Python Framework',
    'long_description': '# fal\n\nfal is a serverless Python runtime that lets you run and scale code in the cloud with no infra management.\n\nWith fal, you can build pipelines, serve ML models and scale them up to many users. You scale down to 0 when you don\'t use any resources.\n\n## Quickstart\n\nFirst, you need to install the `fal` package. You can do so using pip:\n```shell\npip install fal\n```\n\nThen you need to authenticate:\n```shell\nfal auth login\n```\n\nYou can also use fal keys that you can get from [our dashboard](https://fal.ai/dashboard/keys).\n\nNow can use the fal package in your Python scripts as follows:\n\n```py\nimport fal\n\n@fal.function(\n    "virtualenv",\n    requirements=["pyjokes"],\n)\ndef tell_joke() -> str:\n    import pyjokes\n\n    joke = pyjokes.get_joke()\n    return joke\n\nprint("Joke from the clouds: ", tell_joke())\n```\n\nA new virtual environment will be created by fal in the cloud and the set of requirements that we passed will be installed as soon as this function is called. From that point on, our code will be executed as if it were running locally, and the joke prepared by the pyjokes library will be returned.\n\n## Next steps\n\nIf you would like to find out more about the capabilities of fal, check out to the [docs](https://fal.ai/docs). You can learn more about persistent storage, function caches and deploying your functions as API endpoints.\n',
    'author': 'Features & Labels',
    'author_email': 'hello@fal.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
