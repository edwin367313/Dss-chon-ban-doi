import hashlib

def hash_password(pw: str) -> str:
    if pw is None:
        return ""
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()
