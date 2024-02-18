# Interactive Session

A Python module to create a Shell session.

## Table of Contents

- [Interactive Session](#interactive-session)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)

## Installation

- clone the repository
- run 
  ```shell
  pip install -r requirements.txt &&
  python setup.py build &&
  python setup.py test &&
  python setup.py install
  ```

## Usage

```python
import interactive_session as m
session = m.InteractiveSession("bash", "exit")
print(session.execute("echo hello"))
session.close()

```

## License

This project is licensed under the MIT License.
