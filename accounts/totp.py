"""RFC 6238 TOTP implementation using only the standard library.

Compatible with Google Authenticator, Microsoft Authenticator, 1Password,
Authy, Bitwarden, etc.
"""
import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote, urlencode

DIGITS = 6
PERIOD = 30


def generate_secret(length=20):
    """Return a random base32 secret (160 bits by default)."""
    return base64.b32encode(secrets.token_bytes(length)).decode("ascii").rstrip("=")


def _decode(secret):
    secret = secret.strip().replace(" ", "").upper()
    padding = "=" * (-len(secret) % 8)
    return base64.b32decode(secret + padding)


def hotp(secret, counter, digits=DIGITS):
    key = _decode(secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10 ** digits)).zfill(digits)


def current_step(now=None):
    return int((now if now is not None else time.time()) // PERIOD)


def verify(secret, code, last_step=None, window=1, now=None):
    """Check a code. Returns the matched time-step, or None.

    `last_step` blocks replay of a code that has already been used.
    `window` allows +/- N steps of clock drift.
    """
    code = (code or "").strip().replace(" ", "")
    if not code.isdigit() or len(code) != DIGITS:
        return None
    step = current_step(now)
    for offset in range(-window, window + 1):
        candidate = step + offset
        if last_step is not None and candidate <= last_step:
            continue
        if hmac.compare_digest(hotp(secret, candidate), code):
            return candidate
    return None


def provisioning_uri(secret, account, issuer):
    label = quote(f"{issuer}:{account}")
    params = urlencode({"secret": secret, "issuer": issuer, "digits": DIGITS, "period": PERIOD})
    return f"otpauth://totp/{label}?{params}"


def format_secret(secret):
    return " ".join(secret[i:i + 4] for i in range(0, len(secret), 4))
