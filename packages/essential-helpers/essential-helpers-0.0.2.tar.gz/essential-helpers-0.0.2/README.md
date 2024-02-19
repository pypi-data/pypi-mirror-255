<p align="center">
    <img src="https://img.shields.io/badge/status-fully%20functional-brightgreen">
</p>

<h1 align="center">🧹 Essential Helpers 🧹</h1>

## Usage

```python
import essential-helpers 
```

### Argument Parsing

Uses the argparse built-in module to parse arguments ran alongside your script.

- Assign your args
```python
from essential-helpers.arguments import ArgumentParser

parser = ArgumentParser()

# Strings
string_arg: tuple = ("-s", "--string-example")
string_help: str = "This is an example string argument, pass in a string after this argument."
parser.add_string_argument(string_arg, string_help)

# Ints
int_arg: str = "-i"
int_help: str = "This is an example int argument, pass in an int after this argument."
parser.add_int_argument(int_arg, int_help)

# Bools
bool_arg: frozenset = {"-b", "--bool"}
bool_help: str = "This is an example bool argument, passing this will set this bool to true."
parser.add_bool_argument(bool_arg, bool_help)
```
*You can pass in a str ("-eg") or a tuple/list/set (["-eg", "--example"])

- Reference them to see if they have been passed in and what values they hold
```python
string_value: str = parser.get_arg("s")
int_value: int = parser.get_arg("int")
is_bool: bool = parser.get_arg("bool")
```
```python
all_args: dict = parser.get_all_args()
string_value: str = all_args.get("s")
int_value: int = all_args.get("int")
is_bool: bool = all_args.get("bool")
```

### Encryption

### Shell Execution

### File Management
 