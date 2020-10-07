from .constants import FERNET_ENCRYPTION_KEY
from cryptography.fernet import Fernet


def encrypt(value):
    f = Fernet(FERNET_ENCRYPTION_KEY)
    encrypted_value = f.encrypt(value.encode('utf-8'))
    encrypted_value = encrypted_value.decode('utf-8')
    return encrypted_value


def decrypt(value):
    f = Fernet(FERNET_ENCRYPTION_KEY)
    decrypted_value = f.decrypt(value.encode('utf-8'))
    decrypted_value = decrypted_value.decode('utf-8')
    return decrypted_value
