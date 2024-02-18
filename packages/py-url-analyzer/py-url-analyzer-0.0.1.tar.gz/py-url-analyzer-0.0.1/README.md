# py-url-analyzer

URL Analyzer is a Python package for analyzing website performance metrics.

## Installation

To install the package, use the `pip install` command:

```bash
pip install py-url-analyzer
```

## Usage

Here's a basic example of how to use `url-analyzer` package:

```python
from url_analyzer import analyze

url = 'criaway.com'

analyze(url).get('load_time')
```

## Testing

To run tests for the url-analyzer package, use the following command:

```bash
python -m unittest url_analyzer_test.py
```

## Contributions

Contributions are welcome! If you find any issues or have ideas to improve the package, feel free to open an issue or submit a pull request.

## License

This package is distributed under the MIT license. See the LICENSE file for more information.
