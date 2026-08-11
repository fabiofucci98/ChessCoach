"""Unit tests for security helpers (security.py)."""
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)


def test_create_and_decode_token_roundtrip():
    token = create_access_token({"sub": "user-123"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    # jwt includes an expiry claim
    assert "exp" in payload


def test_decode_invalid_token_returns_none():
    assert decode_token("not.a.jwt") is None
    assert decode_token("") is None
