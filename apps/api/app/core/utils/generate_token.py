import secrets
import hashlib

def generate_verification_token():
    raw_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    return raw_token, token_hash
