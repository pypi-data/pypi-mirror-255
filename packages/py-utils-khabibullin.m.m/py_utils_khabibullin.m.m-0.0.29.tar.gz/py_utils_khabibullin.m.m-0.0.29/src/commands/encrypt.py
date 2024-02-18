import base64
import json
from cryptography.fernet import Fernet

from commands.const import DATA_FILE


def encrypt(key: str):
    if not key:
        raise ValueError("Key is not set")
    if len(key) > 32:
        raise ValueError("Key should not be longer then 32 characters")
    elif len(key) < 32:
        key = key.ljust(32, '8')
        

    key = base64.urlsafe_b64encode(key.encode())

    fernet = Fernet(key)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        data = json.dumps(data)
        encrypted_data = fernet.encrypt(data.encode())

    with open(f"{DATA_FILE}_enc", "w") as f:
        f.write(encrypted_data.decode())
