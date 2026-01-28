"""
GOATCRD Encryption Module
AES-256 encryption for PII data at rest
"""
import base64
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


def _get_encryption_key() -> bytes:
    """
    Derive encryption key from secret.
    Uses PBKDF2 to derive a Fernet-compatible key from the app secret.
    """
    # Use a static salt (in production, store this securely)
    salt = b"goatcrd_encryption_salt_v1"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    
    key = base64.urlsafe_b64encode(
        kdf.derive(settings.secret_key.encode())
    )
    return key


def _get_fernet() -> Fernet:
    """Get Fernet instance with derived key."""
    return Fernet(_get_encryption_key())


def encrypt_pii(plaintext: str) -> str:
    """
    Encrypt a PII string value.
    
    Args:
        plaintext: The sensitive data to encrypt
        
    Returns:
        Base64-encoded encrypted string with 'ENC:' prefix
    """
    if not plaintext:
        return plaintext
    
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return f"ENC:{base64.urlsafe_b64encode(encrypted).decode()}"


def decrypt_pii(encrypted_value: str) -> str:
    """
    Decrypt a PII string value.
    
    Args:
        encrypted_value: The encrypted data (with 'ENC:' prefix)
        
    Returns:
        Decrypted plaintext string
        
    Raises:
        ValueError: If decryption fails or data is corrupted
    """
    if not encrypted_value or not encrypted_value.startswith("ENC:"):
        return encrypted_value  # Return as-is if not encrypted
    
    try:
        fernet = _get_fernet()
        encrypted_bytes = base64.urlsafe_b64decode(
            encrypted_value[4:].encode()
        )
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except (InvalidToken, ValueError) as e:
        raise ValueError(f"Failed to decrypt PII data: {e}")


def encrypt_dict_pii(data: dict, pii_fields: list[str]) -> dict:
    """
    Encrypt specified PII fields in a dictionary.
    
    Args:
        data: Dictionary containing data
        pii_fields: List of field paths to encrypt (dot notation for nested)
        
    Returns:
        Dictionary with specified fields encrypted
    """
    result = data.copy()
    
    for field in pii_fields:
        parts = field.split(".")
        current = result
        
        for i, part in enumerate(parts[:-1]):
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                break
        
        final_key = parts[-1]
        if final_key in current and isinstance(current[final_key], str):
            current[final_key] = encrypt_pii(current[final_key])
    
    return result


def decrypt_dict_pii(data: dict, pii_fields: list[str]) -> dict:
    """
    Decrypt specified PII fields in a dictionary.
    
    Args:
        data: Dictionary containing encrypted data
        pii_fields: List of field paths to decrypt (dot notation for nested)
        
    Returns:
        Dictionary with specified fields decrypted
    """
    result = data.copy()
    
    for field in pii_fields:
        parts = field.split(".")
        current = result
        
        for i, part in enumerate(parts[:-1]):
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                break
        
        final_key = parts[-1]
        if final_key in current and isinstance(current[final_key], str):
            if current[final_key].startswith("ENC:"):
                current[final_key] = decrypt_pii(current[final_key])
    
    return result


# Default PII fields for intake data
INTAKE_PII_FIELDS = [
    "ssn",
    "ssn_last_four",
    "email",
    "phone",
    "date_of_birth",
    "bank_account_number",
    "routing_number",
]


def encrypt_intake_pii(intake_data: dict) -> dict:
    """Encrypt standard PII fields in intake data."""
    return encrypt_dict_pii(intake_data, INTAKE_PII_FIELDS)


def decrypt_intake_pii(intake_data: dict) -> dict:
    """Decrypt standard PII fields in intake data."""
    return decrypt_dict_pii(intake_data, INTAKE_PII_FIELDS)


class PIIEncryptionError(Exception):
    """Raised when PII encryption/decryption fails."""
    pass
