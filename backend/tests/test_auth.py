import pytest
from app.auth.auth_service import hash_password, verify_password, create_access_token, decode_token
from app.models.user import UserRole


def test_password_hashing():
    password = "TestPassword@123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "42", "role": UserRole.STUDENT.value}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = decode_token(token)
    assert decoded["sub"] == "42"
    assert decoded["role"] == UserRole.STUDENT.value
    assert "exp" in decoded


def test_invalid_jwt_token():
    with pytest.raises(Exception):
        decode_token("invalid.jwt.token")
