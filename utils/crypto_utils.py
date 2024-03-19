from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import cryptography.hazmat.backends.openssl.backend as backend


def generate_crypto_keys():
    """Generate private and public key

    Returns:
        RSAPublicKey, RSAPrivateKey: Private Key, Public Key
    """

    # Generate keys
    keySize = 4096
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=keySize, backend=backend
    )

    return key, key.public_key()


def public_bytes(key: RSAPublicKey) -> bytes:
    """Serialize `RSAPublicKey in bytes`

    Args:
        key (RSAPublicKey): The public key to serialize

    Returns:
        bytes: The serialized key
    """
    return key.public_bytes(
        crypto_serialization.Encoding.PEM, crypto_serialization.PublicFormat.PKCS1
    )


def private_bytes(key: RSAPrivateKey) -> bytes:
    """Serialize `RSAPrivateKey in bytes`

    Args:
        key (RSAPrivateKey): The private key to serialize

    Returns:
        bytes: The serialized key
    """
    return key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        crypto_serialization.NoEncryption(),
    )
