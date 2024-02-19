# Safeloader

Safeloader is a simple Python module that creates a straightforward loading text message while your code executes.

## Instalation

Use the package manager [pip](https://pip.pypa.io/en/stable) to install.

```bash
pip install safeloader
```

## Usage

```python
from safeloader import Loader
simple_loader = Loader()
simple_loader.start()
# Code to execute while loading.
simple_loader.stop()
```

## License
[MIT](https://choosealicense.com/licenses/mit/)