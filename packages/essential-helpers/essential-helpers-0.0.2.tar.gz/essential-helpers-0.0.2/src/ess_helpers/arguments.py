# DEPENDENCIES
## Built-in
from argparse import ArgumentParser
from typing import Callable


# PARSER TYPES
def _string_argument(
    parser: ArgumentParser,
    arg_names: (str, tuple),
    help_text: str,
    required: bool
) -> None:
    parser.add_argument(*arg_names, type=str, required=required, help=help_text)

def _int_argument(
    parser: ArgumentParser,
    arg_names: (str, tuple),
    help_text: str,
    required: bool
) -> None:
    parser.add_argument(*arg_names, type=int, required=required, help=help_text)

def _bool_argument(
    parser: ArgumentParser,
    arg_names: (str, tuple),
    help_text: str,
    required: bool
) -> None:
    parser.add_argument(*arg_names, action='store_true', required=required, help=help_text)


# INTERFACE
def _add_argument_type(
    parser: ArgumentParser,
    type_argument: Callable[[ArgumentParser, (str, tuple), str], None],
    arg_names: (str, tuple),
    help_text: str,
    required: bool
) -> None:
    type_argument(parser, arg_names, help_text, required)


# IMPLEMENTATION
class Arguments:
    def __init__(self) -> None:
        self.parser = ArgumentParser()
        self.arguments: dict = {}

    # Assignment
    def add_string_argument(
        self,
        arg_names: (str, tuple),
        help_text: str,
        required: bool = False
    ) -> None:
        _add_argument_type(self.parser, _string_argument, arg_names, help_text, required)

    def add_int_argument(
        self,
        arg_names: (str, tuple),
        help_text: str,
        required: bool = False
    ) -> None:
        _add_argument_type(self.parser, _int_argument, arg_names, help_text, required)

    def add_bool_argument(
        self,
        arg_names: (str, tuple),
        help_text: str,
        required: bool = False
    ) -> None:
        _add_argument_type(self.parser, _bool_argument, arg_names, help_text, required)

    # Retrieval
    def _assign_arguments(self) -> None:
        if not self.arguments:
            self.arguments: dict = vars(self.parser.parse_args())

    def get_arg(self, arg_name: str) -> (str, int, bool, None):
        self._assign_arguments()
        return self.arguments.get(arg_name)

    def get_all_args(self) -> dict:
        self._assign_arguments()
        return self.arguments
