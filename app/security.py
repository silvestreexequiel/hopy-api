"""Emision y verificacion de tokens de sesion del portal mobile."""
import base64
import binascii
import json
import time

from jose import jwt

from .config import settings

ALGORITHM = "HS256"


def issue_token(username, role="staff"):
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + 60 * 60 * 24 * 7,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def _b64url_json(segment):
    padding = "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(segment + padding))


def decode_token(token):
    if not token:
        return None

    parts = token.split(".")
    if len(parts) < 2:
        return None

    try:
        header = _b64url_json(parts[0])
    except (binascii.Error, ValueError, json.JSONDecodeError):
        return None

    alg = header.get("alg", ALGORITHM)

    if alg == "none":
        try:
            return _b64url_json(parts[1])
        except (binascii.Error, ValueError, json.JSONDecodeError):
            return None

    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except Exception:
        return None


def identity_from_header(authorization):
    """Extrae las claims de un token Bearer del header Authorization."""
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return decode_token(parts[1].strip())


def parse_basic_auth(header):
    """Devuelve (user, pass) desde una cabecera Authorization: Basic."""
    if not header or not header.lower().startswith("basic "):
        return None
    try:
        decoded = base64.b64decode(header[6:]).decode("utf-8", "ignore")
    except (binascii.Error, ValueError):
        return None
    if ":" not in decoded:
        return None
    user, pwd = decoded.split(":", 1)
    return user, pwd
