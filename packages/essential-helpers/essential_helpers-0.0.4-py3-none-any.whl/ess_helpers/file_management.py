# DEPENEDNCIES
## Built-in
import json
import pickle
import os
## Local
from ess_helpers.exceptions.error_handling import exit_on_error
from ess_helpers.exceptions.file_management import (
    BytesFromJsonFileError,
    ReadBytesFileError,
    WriteFileError,
    DeleteFileError
)


# VALIDATION
def file_exists(file_path: str, exit_from_error: bool = False, error_message: str = "") -> None:
    exists: bool = os.path.exists(file_path)
    if not error_message:
        error_message = f"Error: {file_path} does not exist"
    if exit_from_error and not exists:
        exit_on_error(error_message)
    return os.path.exists(file_path)

# RETRIEVAL
def bytes_from_jsonfile(file_path: str) -> bytes:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data: dict = json.load(file)
            data: bytes = pickle.dumps(json_data)
        return data
    except (FileNotFoundError, json.JSONDecodeError, pickle.PickleError, Exception) as error:
        raise BytesFromJsonFileError(file_path) from error


def read_bytesfile(file_path: str) -> bytes:
    try:
        with open(file_path, 'rb') as file:
            data: bytes = file.read()
        return data
    except (FileNotFoundError, Exception) as error:
        raise ReadBytesFileError(file_path) from error


# MANIPULATION
def destroy_file(file_path: str) -> None:
    try:
        with open(file_path, 'wb') as file:
            file.write(os.urandom(os.path.getsize(file_path)))
    except (FileNotFoundError, PermissionError, Exception) as error:
        raise WriteFileError(file_path) from error

    try:
        os.remove(file_path)
    except (FileNotFoundError, PermissionError, Exception) as error:
        raise DeleteFileError(file_path) from error

def bytes_to_file(file_path: str, contents: bytes) -> None:
    try:
        with open(file_path, 'wb') as file:
            file.write(contents)
    except (FileNotFoundError, PermissionError, Exception) as error:
        raise WriteFileError(file_path) from error

def json_to_file(file_path: str, contents: dict) -> None:
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(contents, file)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError, TypeError, Exception) as error:
        raise WriteFileError(file_path) from error
