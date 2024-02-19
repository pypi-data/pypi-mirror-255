# DEPENEDNCIES
## Built-in
import pickle
## Third Party
import nacl.secret
from nacl.secret import SecretBox
import nacl.utils
from nacl.utils import EncryptedMessage
## Local
from ess_helpers.exceptions.encryption import (
    EncryptBytesError,
    DecryptBytesError,
    EncodeKeyError,
    DecodeKeyError
)


# INSTANTIALISATION
def get_box(key: bytes) -> SecretBox:
    box: SecretBox = nacl.secret.SecretBox(key)
    return box


# ENCRYPTION
def generate_access_key() -> bytes:
    print("Generating Access Key...")
    key: bytes = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    return key

def encrypt_bytes(key: bytes, data: bytes) -> bytes:
    try:
        box: SecretBox = get_box(key)
        encrypted_data: EncryptedMessage = box.encrypt(data)
        serialised_data: bytes = pickle.dumps(encrypted_data)
        return serialised_data
    except Exception as error:
        raise EncryptBytesError() from error


# DECRYPTION
def decrypt_bytes(key: bytes, serialised_data: bytes) -> bytes:
    try:
        box: SecretBox = get_box(key)
        encrypted_data: EncryptedMessage = pickle.loads(serialised_data)
        data: bytes = box.decrypt(encrypted_data)
        return data
    except Exception as error:
        raise DecryptBytesError() from error


# CONVERSION
def encode_key(key: bytes) -> str:
    try:
        key_string: str = key.hex()
        return key_string
    except Exception as error:
        raise EncodeKeyError() from error

def decode_key(key_string: str) -> bytes:
    try:
        key: bytes = bytes.fromhex(key_string)
        return key
    except Exception as error:
        raise DecodeKeyError() from error
