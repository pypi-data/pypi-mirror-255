"""
# Utilities distributed with Client Package

## Contents

- `container_utils.py`
- `python_utils.py`
- `iter_utils.py`
- `type_utils.py`
- `annotations.py` - Helpers for dealing with types when
  `future.__annotations__` is used.
- `types.py` - New types and working replacements for `typing.*` types.
- `func.py` - Utilities for deaing with functions and methods.
- `overload.py` - Method overloading decorator.
- `doc.py` - Docstring utilities.
- `debug.py` - Printing and debugging utilities.
- TODO: various others.

## Avoiding Circular Dependencies

Dependency diagram. In the below, any file A that appears below file B is not
allowed to import B.

  doc.py debug.py container_utils.py [independent from below]

  ----

  overload.py

  func.py

  types.py

  annotations.py

  type_utils.py iter_utils.py

  python_utils.py

## Logging

Can use this logger at top-level if no class is used:

`python
  logger = logging.getLogger(name=__name__)
`

Or as part of a class:

`python
  def __init__(self, ...):
    ...
    self.logger = logging.getLogger(name=self.__name__)
    ...
`

"""