# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geneagrapher_core']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.9.3,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'types-beautifulsoup4>=4.11.6.4,<5.0.0.0']

setup_kwargs = {
    'name': 'geneagrapher-core',
    'version': '0.1.3',
    'description': 'Functions for getting records and building graphs from the Math Genealogy Project.',
    'long_description': '# geneagrapher-core [![Continuous Integration Status](https://github.com/davidalber/geneagrapher-core/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/davidalber/geneagrapher-core/actions/workflows/ci.yaml/badge.svg?branch=main) [![Live Tests Status](https://github.com/davidalber/geneagrapher-core/actions/workflows/live-tests.yaml/badge.svg?branch=main)](https://github.com/davidalber/geneagrapher-core/actions/workflows/live-tests.yaml/badge.svg?branch=main) [![Documentation Status](https://readthedocs.org/projects/geneagrapher-core/badge/?version=latest)](https://geneagrapher-core.readthedocs.io/en/latest/?badge=latest)\n\n## Overview\nGeneagrapher is a tool for extracting information from the\n[Mathematics Genealogy Project](https://www.mathgenealogy.org/) to\nform a math family tree, where connections are between advisors and\ntheir students.\n\nThis package contains the core data-grabbing and manipulation\nfunctions needed to build a math family tree. The functionality here\nis low level and intended to support the development of other\ntools. If you just want to build a geneagraph, take a look at\n[Geneagrapher](https://github.com/davidalber/geneagrapher). If you\nwant to get mathematician records and use them in code, then this\nproject may be useful to you.\n\n## Documentation\nDocumentation about how to call into this package\'s functions can be\nfound at http://geneagrapher-core.readthedocs.io/.\n\n## Development\nDependencies in this package are managed by\n[Poetry](https://python-poetry.org/). Thus, your Python environment\nwill need Poetry installed. Install all dependencies with:\n\n```sh\n$ poetry install\n```\n\nSeveral development commands are runnable with `make`:\n- `make fmt` (also `make black` and `make format`) formats code using\n  black\n- `make format-check` runs black and reports if the code passes\n  formatting checks without making changes\n- `make lint` (also `make flake8` and `make flake`) does linting\n- `make mypy` (also `make types`) checks the code for typing violations\n- `make test` runs automated tests\n- `make check` does code formatting (checking, not modifying),\n  linting, type checking, and testing in one command; if this command\n  does not pass, CI will not pass\n\n## Releasing New Versions\n\n1. Increase the version in pyproject.toml (e.g., [ed80c2c](https://github.com/davidalber/geneagrapher-core/commit/ed80c2c568605f0eab3c3b8a9bf9d7d14aaf1495)).\n1. Add an entry for the new version in CHANGELOG.md (e.g., [bf2931a](https://github.com/davidalber/geneagrapher-core/commit/bf2931a2b602c692cf690dd55b0809489c457e7c)).\n1. Push changes.\n1. Tag the new version with message "Release VERSION".\n   ```bash\n   $ git tag -s vVERSION COMMIT_SHA\n   ```\n1. Push the tag.\n   ```bash\n   $ git push origin vVERSION\n   ```\n1. Build the distribution.\n   ```bash\n   $ poetry build\n   ```\n1. Publish release to Test PyPI (this assumes that Poetry has been\n   configured with the Test PyPI URL).\n   ```bash\n   $ poetry publish -r testpypi\n   ```\n1. Publish release to PyPI.\n   ```bash\n   $ poetry publish\n   ```\n1. Create [new\n   release](https://github.com/davidalber/geneagrapher-core/releases/new).\n',
    'author': 'David Alber',
    'author_email': 'alber.david@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/davidalber/geneagrapher-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
