# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src',
 'harlequin_duckdb': 'src/harlequin_duckdb',
 'harlequin_sqlite': 'src/harlequin_sqlite'}

packages = \
['harlequin',
 'harlequin.autocomplete',
 'harlequin.components',
 'harlequin_duckdb',
 'harlequin_sqlite']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'duckdb>=0.8.0',
 'platformdirs>=3.10,<5.0',
 'questionary>=2.0.1,<3.0.0',
 'rich-click>=1.7.1,<2.0.0',
 'shandy-sqlfmt>=0.19.0',
 'textual-fastdatatable==0.7.0',
 'textual-textarea==0.11.0',
 'textual==0.49.0',
 'tomlkit>=0.12.3,<0.13.0']

extras_require = \
{':python_full_version < "3.10.0"': ['importlib_metadata>=4.6.0'],
 ':python_full_version < "3.11.0"': ['tomli>=2.0.1,<3.0.0'],
 'bigquery': ['harlequin-bigquery>=1.0,<2.0'],
 'databricks': ['harlequin-databricks>=0.1,<0.2'],
 'mysql': ['harlequin-mysql>=0.1,<0.2'],
 'odbc': ['harlequin-odbc>=0.1,<0.2'],
 'postgres': ['harlequin-postgres>=0.2,<0.3'],
 's3': ['boto3>=1.34.22,<2.0.0'],
 'trino': ['harlequin-trino>=0.1,<0.2']}

entry_points = \
{'console_scripts': ['harlequin = harlequin.cli:harlequin'],
 'harlequin.adapter': ['duckdb = harlequin_duckdb:DuckDbAdapter',
                       'sqlite = harlequin_sqlite:HarlequinSqliteAdapter'],
 'pygments.styles': ['harlequin = harlequin.colors:HarlequinPygmentsStyle']}

setup_kwargs = {
    'name': 'harlequin',
    'version': '1.14.0',
    'description': 'The SQL IDE for Your Terminal.',
    'long_description': '# Harlequin\n\n[![PyPI](https://img.shields.io/pypi/v/harlequin)](https://pypi.org/project/harlequin/)\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/harlequin)\n![Runs on Linux | MacOS | Windows](https://img.shields.io/badge/runs%20on-Linux%20%7C%20MacOS%20%7C%20Windows-blue)\n\nThe SQL IDE for Your Terminal.\n\n![Harlequin](./harlequin.svg)\n\n## Installing Harlequin\n\nAfter installing Python 3.8 or above, install Harlequin using `pip` or `pipx` with:\n\n```bash\npipx install harlequin\n```\n\n## Using Harlequin with DuckDB\n\nFrom any shell, to open one or more DuckDB database files:\n\n```bash\nharlequin "path/to/duck.db" "another_duck.db"\n```\n\nTo open an in-memory DuckDB session, run Harlequin with no arguments:\n\n```bash\nharlequin\n```\n\nIf you want to control the version of DuckDB that Harlequin uses, see the [Troubleshooting](https://harlequin.sh/docs/troubleshooting/duckdb-version-mismatch) page.\n\n## Using Harlequin with SQLite and Other Adapters\n\nHarlequin also ships with a SQLite3 adapter. You can open one or more SQLite database files with:\n\n```bash\nharlequin -a sqlite "path/to/sqlite.db" "another_sqlite.db"\n```\n\nLike DuckDB, you can also open an in-memory database by omitting the paths:\n\n```bash\nharlequin -a sqlite\n```\n\nOther adapters can be installed using `pip install <adapter package>` or `pipx inject harlequin <adapter package>`, depending on how you installed Harlequin. For a list of known adapters provided either by the Harlequin maintainers or the broader community, see the [adapters](https://harlequin.sh/docs/adapters) page in the docs.\n\n## Getting Help\n\nTo view all command-line options for Harlequin and all installed adapters, after installation, simply type:\n\n```bash\nharlequin --help\n```\n\nTo view a list of all key bindings (keyboard shortcuts) within the app, press <Key>F1</Key>. You can also view this list outside the app [in the docs](https://harlequin.sh/docs/bindings).\n\nCOLOR, KEY BINDING, OR COPY-PASTE PROBLEMS? See [Troubleshooting](https://harlequin.sh/docs/troubleshooting/index) in the docs. \n\n## More info at [harlequin.sh](https://harlequin.sh)\n\nVisit [harlequin.sh](https://harlequin.sh) for an overview of features and full documentation.\n\n## Contributing\n\nThanks for your interest in Harlequin! Harlequin is primarily maintained by [Ted Conbeer](https://github.com/tconbeer), but he welcomes all contributions and is looking for additional maintainers!\n\n### Providing Feedback\n\nWe\'d love to hear from you! [Open an Issue](https://github.com/tconbeer/harlequin/issues/new) to request new features, report bugs, or say hello.\n\n### Setting up Your Dev Environment and Running Tests\n\n1. Install Poetry v1.2 or higher if you don\'t have it already. You may also need or want pyenv, make, and gcc.\n1. Fork this repo, and then clone the fork into a directory (let\'s call it `harlequin`), then `cd harlequin`.\n1. Use `poetry install --sync` to install the project (editable) and its dependencies (including all test and dev dependencies) into a new virtual env.\n1. Use `poetry shell` to spawn a subshell.\n1. Type `make` to run all tests and linters, or run `pytest`, `black .`, `ruff . --fix`, and `mypy` individually.\n\n### Opening PRs\n\n1. PRs should be motivated by an open issue. If there isn\'t already an issue describing the feature or bug, [open one](https://github.com/tconbeer/harlequin/issues/new). Do this before you write code, so you don\'t waste time on something that won\'t get merged.\n2. Ideally new features and bug fixes would be tested, to prevent future regressions. Textual provides a test harness that we use to test features of Harlequin. You can find some examples in the `tests` directory of this project. Please include a test in your PR, but if you can\'t figure it out, open a PR to ask for help.\n2. Open a PR from your fork to the `main` branch of `tconbeer/harlequin`. In the PR description, link to the open issue, and then write a few sentences about **why** you wrote the code you did: explain your design, etc.\n3. Ted may ask you to make changes, or he may make them for you. Don\'t take this the wrong way -- he values your contributions, but he knows this isn\'t your job, either, so if it\'s faster for him, he may push a commit to your branch or create a new branch from your commits.\n',
    'author': 'Ted Conbeer',
    'author_email': 'tconbeer@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://harlequin.sh',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
