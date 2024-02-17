# pydBuilder
pydBuilder is a simple utility for converting Python scripts to `pyd` files using Cython.

## Installation
```bash
pip install pydbuilder
```

## Using

**Step 1**: Create a Python script to compile using the module
```python
def difference(a: int, b: int) -> str:
    result = abs(a - b) / min(a, b)
    result = result * 100
    return f'{result:.2f}%'

print(difference(3432, 2831))
```

**Step 2**: Use the module to automatically compile the script
```bash
pydbuilder difference.py
```
or
```bash
pydbuilder path/to/difference.py
```

**Step 3**: Use the compiled file in the code
```python
from difference import difference

print(difference(3432, 2831))
```