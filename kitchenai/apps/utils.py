
from hashlib import sha256

def hash_to_int(value):
    """Convert a string to a deterministic integer."""
    hash_obj = sha256(str(value).encode())
    hash_hex = hash_obj.hexdigest()[:8]
    return int(hash_hex, 16)