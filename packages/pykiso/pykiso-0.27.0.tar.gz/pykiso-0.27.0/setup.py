# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pykiso',
 'pykiso.interfaces',
 'pykiso.lib',
 'pykiso.lib.auxiliaries',
 'pykiso.lib.auxiliaries.instrument_control_auxiliary',
 'pykiso.lib.auxiliaries.simulated_auxiliary',
 'pykiso.lib.auxiliaries.udsaux',
 'pykiso.lib.auxiliaries.udsaux.common',
 'pykiso.lib.connectors',
 'pykiso.lib.connectors.cc_pcan_can',
 'pykiso.lib.connectors.cc_socket_can',
 'pykiso.lib.robot_framework',
 'pykiso.pytest_plugin',
 'pykiso.test_coordinator',
 'pykiso.test_result',
 'pykiso.test_setup',
 'pykiso.tool',
 'pykiso.tool.pykiso_to_pytest',
 'pykiso.tool.testrail']

package_data = \
{'': ['*'],
 'pykiso.test_result': ['templates/*'],
 'pykiso.tool.pykiso_to_pytest': ['templates/*']}

install_requires = \
['Jinja2>=2.11.0,<4.0.0',
 'MarkupSafe>=2.0.1,<2.1.0',
 'PyYAML>=6.0,<7.0',
 'brainstem',
 'click>=7.0.0,<9.0.0',
 'defusedxml>=0.7.1,<0.8.0',
 'hidapi>=0.12,<0.15',
 'packaging',
 'robotframework==3.2.2',
 'tabulate>=0.8.9,<0.10.0',
 'unittest-xml-reporting>=3.2.0,<4.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.12,<7.0'],
 ':python_version >= "3.5" and python_version < "4.0"': ['pyreadline3>=3.4.1,<4.0.0'],
 ':python_version >= "3.8" and python_version < "4.0"': ['cantools>=39.4.2,<40.0.0'],
 'all': ['rich>=13.2.0,<14.0.0',
         'requests>=2.28.2,<3.0.0',
         'isort>=5.11.4',
         'black',
         'pylink-square>=1.2.0,<1.3.0',
         'pykiso-python-uds>=3.2.0,<3.3.0',
         'pyserial>=3.0,<4.0',
         'PyVISA>=1.12.0,<2.0.0',
         'PyVISA-py>=0.5.3,<0.6.0',
         'python-can[pcan,vector]>=4.2.1,<5.0.0',
         'grpcio>=1.0.0,<2.0.0',
         'protobuf>=4.24.2,<5.0.0'],
 'can': ['pykiso-python-uds>=3.2.0,<3.3.0',
         'python-can[pcan,vector]>=4.2.1,<5.0.0'],
 'debugger': ['pylink-square>=1.2.0,<1.3.0'],
 'grpc': ['grpcio>=1.0.0,<2.0.0', 'protobuf>=4.24.2,<5.0.0'],
 'instrument': ['PyVISA>=1.12.0,<2.0.0', 'PyVISA-py>=0.5.3,<0.6.0'],
 'plugins': ['pylink-square>=1.2.0,<1.3.0',
             'pykiso-python-uds>=3.2.0,<3.3.0',
             'pyserial>=3.0,<4.0',
             'PyVISA>=1.12.0,<2.0.0',
             'PyVISA-py>=0.5.3,<0.6.0',
             'python-can[pcan,vector]>=4.2.1,<5.0.0'],
 'pykitest': ['isort>=5.11.4', 'black'],
 'serial': ['pyserial>=3.0,<4.0'],
 'testrail': ['rich>=13.2.0,<14.0.0', 'requests>=2.28.2,<3.0.0']}

entry_points = \
{'console_scripts': ['instrument-control = '
                     'pykiso.lib.auxiliaries.instrument_control_auxiliary.instrument_control_cli:main',
                     'pykiso = pykiso.cli:main',
                     'pykiso-tags = pykiso.tool.show_tag:main',
                     'pykitest = pykiso.tool.pykiso_to_pytest.cli:main',
                     'testrail = pykiso.tool.testrail.cli:cli_testrail'],
 'pytest11': ['pytest_kiso = pykiso.pytest_plugin']}

setup_kwargs = {
    'name': 'pykiso',
    'version': '0.27.0',
    'description': 'Embedded integration testing framework.',
    'long_description': '[![License](https://img.shields.io/badge/Licence-Eclipse%20Public%20License%202.0-lightgrey)](https://opensource.org/licenses/EPL-2.0)\n[![Platforms](https://img.shields.io/badge/Platforms-win64%20linux64%20osx64-lightgrey)]()\n[![Supported python version](https://img.shields.io/pypi/pyversions/pykiso)]()\n[![Build status](https://img.shields.io/jenkins/build?jobUrl=https%3A%2F%2Fci.eclipse.org%2Fkiso-testing%2Fjob%2Fkiso-testing%2Fjob%2Fmaster%2F)](https://ci.eclipse.org/kiso-testing/job/kiso-testing/job/master/)\n[![Documentation Status](https://readthedocs.org/projects/kiso-testing/badge/?version=latest)](https://kiso-testing.readthedocs.io/en/latest/?badge=latest)\n[![Test results](https://img.shields.io/jenkins/tests?compact_message&failed_label=failed&jobUrl=https%3A%2F%2Fci.eclipse.org%2Fkiso-testing%2Fjob%2Fkiso-testing%2Fjob%2Fmaster%2F&passed_label=passed&skipped_label=skipped)](https://ci.eclipse.org/kiso-testing/job/kiso-testing/job/master/)\n[![codecov](https://codecov.io/gh/eclipse/kiso-testing/branch/master/graph/badge.svg?token=IBKQ700ABS)](https://codecov.io/gh/eclipse/kiso-testing)\n[![CodeFactor](https://www.codefactor.io/repository/github/eclipse/kiso-testing/badge)](https://www.codefactor.io/repository/github/eclipse/kiso-testing)\n[![Last commit](https://img.shields.io/github/last-commit/eclipse/kiso-testing)]()\n[![Commits since latest version](https://img.shields.io/github/commits-since/eclipse/kiso-testing/latest/master)]()\n\n# PyKiso\n\n![Optional Text](./docs/images/pykiso_logo.png)\n\n## Introduction ##\n\n**pykiso** is an integration test framework. With it, it is possible to write\n* Whitebox integration tests directly on my target device\n* Graybox integration tests to make sure the communication-link with my target device is working as expected\n* Blackbox integration tests to make sure my external device interfaces are working as expected\n\nThe project will contain:\n* The core python framework (this repository)\n* Framework plugins that are generic enough to be integrated as "native" (this repository)\n* Additional "testApps" for different targets platforms (e.g. stm32, ...) or languages (C, C++, ...) . It could be pure SW or also HW (other repositories)\n\n## Link to Eclipse Project\nhttps://projects.eclipse.org/projects/iot.kiso-testing\n\n## Requirements ##\n\n* Python 3.7+\n* pip/poetry (used to get the rest of the requirements)\n\n## Install ##\n\n```bash\npip install pykiso # Core framework\npip install pykiso[plugins] # For installing all plugins\npip install pykiso[all] # For installing all what we have to offer\n```\n\n[Poetry](https://python-poetry.org/) is more appropriate for developers as it automatically creates virtual environments.\n\n```bash\ncd kiso-testing\npoetry install --all-extras\npoetry shell\n```\n\n### Pre-Commit\n\nTo improve code-quality, a configuration of [pre-commit](https://pre-commit.com/) hooks are available.\nThe following pre-commit hooks are used:\n\n- ruff-format\n- flake8\n- isort\n- trailing-whitespace\n- end-of-file-fixer\n- check-docstring-first\n- check-json\n- check-added-large-files\n- check-yaml\n- debug-statements\n\nIf you don\'t have pre-commit installed, you can get it using pip:\n\n```bash\npip install pre-commit\n```\n\nStart using the hooks with\n\n```bash\npre-commit install\n```\n\n## Commit message convention\n\nCommits are sorted into multiple categories based on keywords that can occur at any position as part of the commit message.\n[Category] Keywords\n* [BREAKING CHANGES] BREAKING CHANGE\n* [Features] feat:\n* [Fixes] fix:\n* [Docs] docs:\n* [Styles] style:\n* [Refactors] refactor!:\n* [Performances] perf:\n* [Tests] test:\n* [Build] build:\n* [Ci] ci:\nEach commit is considered only once according to the order of the categories listed above. Merge commits are ignored.\n\nThe tool commitizen can help you to create commits which follows these standards.\n```bash\n# if not yet installed:\npip install -U commitizen==2.20.4\n# helps you to create a commit:\ncz commit\n# or use equivalent short variant:\ncz c\n```\n\n## Generate Changelog\n\nAfter you installed the dev dependencies from the pipfile you are able to\nautogenerate the Changelog.\n\n```bash\ninvoke changelog\n```\n\n## Usage ##\n\nOnce installed the application is bound to `pykiso`, it can be called with the following arguments:\n\n```bash\nUsage: pykiso [OPTIONS]\n\n  Embedded Integration Test Framework - CLI Entry Point.\n\n  TAG Filters: any additional option to be passed to the test as tag through\n  the pykiso call. Multiple values must be separated with a comma.\n\n  For example: pykiso -c your_config.yaml --branch-level dev,master --variant\n  delta\n\nOptions:\n  -c, --test-configuration-file FILE\n                                  path to the test configuration file (in YAML\n                                  format)  [required]\n  -l, --log-path PATH             path to log-file or folder. If not set will\n                                  log to STDOUT\n  --log-level [DEBUG|INFO|WARNING|ERROR]\n                                  set the verbosity of the logging\n  --junit                         enables the generation of a junit report\n  --text                          default, test results are only displayed in\n                                  the console\n  --step-report PATH              generate the step report at the specified\n                                  path\n  --failfast                      stop the test run on the first error or\n                                  failure\n  -v, --verbose                   activate the internal framework logs\n  -p, --pattern TEXT              test filter pattern, e.g. \'test_suite_1.py\'\n                                  or \'test_*.py\'. Or even more granularly\n                                  \'test_suite_1.py::test_class::test_name\'\n  --version                       Show the version and exit.\n  -h, --help                      Show this message and exit.\n  --logger                        Change the logger class used in pykiso, value\n                                  is the import path to the logger class, example\n                                  \'logging.Logger\'\n```\n\nSuitable config files are available in the `examples` folder.\n\n### Demo using example config ##\n\n```bash\ninvoke run\n```\n\n### Running the Tests ##\n\n```bash\ninvoke test\n```\n\nor\n\n```bash\npytest\n```\n',
    'author': 'Sebastian Fischer',
    'author_email': 'sebastian.fischer@de.bosch.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://pypi.org/project/pykiso/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
