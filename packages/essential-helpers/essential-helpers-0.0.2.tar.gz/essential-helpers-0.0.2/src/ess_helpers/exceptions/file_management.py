class BytesFromJsonFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to load bytes from json file: {file_path}"
        super().__init__(self.error_message)

class ReadBytesFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to read bytes from file: {file_path}"
        super().__init__(self.error_message)

class WriteFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to write to file: {file_path}"
        super().__init__(self.error_message)

class DeleteFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to delete file: {file_path}"
        super().__init__(self.error_message)