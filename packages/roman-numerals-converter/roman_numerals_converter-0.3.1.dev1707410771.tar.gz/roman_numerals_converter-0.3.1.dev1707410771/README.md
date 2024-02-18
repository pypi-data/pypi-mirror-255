[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/Ceddicedced/roman-numeral-converter/graph/badge.svg?token=04M8K8SJX8)](https://codecov.io/gh/Ceddicedced/roman-numeral-converter)
# Roman Numeral Converter

This Python CLI (Command-Line Interface) project, developed for the "Moderne Softwareentwicklung" course, offers an efficient way to convert integers to Roman numerals and vice versa. Built with the Click library, it provides a user-friendly experience on the command line.

## Features

- **Integer to Roman Numeral Conversion**: Convert integers within the range of 1 to 3999 into Roman numerals.
- **Roman Numeral to Integer Conversion**: Translate valid Roman numerals back into integers.

## Getting Started

### Prerequisites

- [Poetry](https://python-poetry.org/) for dependency management.
- [pip](https://pip.pypa.io/en/stable/) for package installation.

### Installation

#### Using Poetry

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repository/roman-numeral-converter.git
   cd roman-numeral-converter
   ```

2. **Install Dependencies**

   ```bash
   poetry install
   ```

#### Using pip

If you prefer to use pip:

```bash
pip install roman-numeral-converter
```

## Usage

Once installed, the CLI can be used as follows:

1. **Convert an Integer to a Roman Numeral**

   Syntax:
   ```bash
   poetry run python -m roman.your_module_name to-roman [number]
   ```
   Replace `[number]` with the integer you wish to convert.

2. **Convert a Roman Numeral to an Integer**

   Syntax:
   ```bash
   poetry run python -m roman.your_module_name from-roman [roman_numeral]
   ```
   Replace `[roman_numeral]` with the Roman numeral you wish to translate.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Acknowledgments

- Thanks to the "Moderne Softwareentwicklung" course team for their guidance.
- [Click](https://click.palletsprojects.com/en/8.0.x/), for making command-line interface creation efficient.
