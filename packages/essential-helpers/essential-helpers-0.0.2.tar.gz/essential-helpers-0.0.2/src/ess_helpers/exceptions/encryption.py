class EncryptBytesError(Exception):
    def __init__(self):
        self.error_message = "Error while trying to encrypt bytes"
        super().__init__(self.error_message)

class DecryptBytesError(Exception):
    def __init__(self):
        self.error_message = "Error while trying to decrypt bytes"
        super().__init__(self.error_message)

class EncodeKeyError(Exception):
    def __init__(self):
        self.error_message = "Error while trying to encode key"
        super().__init__(self.error_message)

class DecodeKeyError(Exception):
    def __init__(self):
        self.error_message = "Error while trying to decode key"
        super().__init__(self.error_message)

## Key
class EncryptFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to encrypt file: {file_path}"
        super().__init__(self.error_message)

class EncryptKeyError(Exception):
    def __init__(self):
        self.error_message = "Error while trying to encrypt key"
        super().__init__(self.error_message)

class DecryptFileError(Exception):
    def __init__(self, file_path: str):
        self.error_message = f"Error while trying to decrypt file: {file_path}"
        super().__init__(self.error_message)