import base64
import json
from cryptography.fernet import Fernet

from commands.const import DATA_FILE


def decrypt(key: str):
    if not key:
        raise ValueError("Key is not set")
    if len(key) > 32:
        raise ValueError("Key should not be longer then 32 characters")
    elif len(key) < 32:
        key = key.ljust(32, '8')

    key = base64.urlsafe_b64encode(key.encode())
    fernet = Fernet(key)

    with open(f"{DATA_FILE}_enc", "r") as f:
        data = f.read()
        decrypted_data = fernet.decrypt(data)

    with open(DATA_FILE, "w") as f:
        data = json.loads(decrypted_data)
        json.dump(data, f, indent=2)
