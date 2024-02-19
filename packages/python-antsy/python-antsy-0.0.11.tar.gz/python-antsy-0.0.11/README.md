[![Release](https://github.com/grupodyd/python-antsy/actions/workflows/release.yml/badge.svg)](https://github.com/grupodyd/python-antsy/actions/workflows/release.yml)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![pypi](https://badge.fury.io/py/python-antsy.svg)](https://pypi.org/project/python-antsy/)
[![PyPI](https://img.shields.io/pypi/pyversions/python-antsy.svg)](https://pypi.python.org/pypi/python-antsy)

# python-antsy
Python package for integration of Antsy in other applications

## Installation

Install from PyPi using [pip](https://pip.pypa.io/en/latest/), a
package manager for Python.

```shell
pip install python-antsy
```

### Test your installation

Try to find the attributes of your authentication token. Save the following code sample to your computer with a text editor. Be sure to replace `refresh_token`.

```python
from antsy import Antsy

# Your Auth Token
client = Antsy(refresh_token="JWT_TOKEN")

client.auth.whoami()
```
