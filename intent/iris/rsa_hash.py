from __future__ import annotations

import hashlib


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RSADigestVerifier:
    """
    Lightweight RSA-style verification scaffold.
    This uses modular exponentiation over a digest-derived integer so the
    registration layer can bind access checks to a public/private key pair.
    """

    def sign_digest(self, digest_hex: str, private_exponent: int, modulus: int) -> int:
        value = int(digest_hex, 16) % modulus
        return pow(value, private_exponent, modulus)

    def verify_digest(self, digest_hex: str, signature: int, public_exponent: int, modulus: int) -> bool:
        expected = int(digest_hex, 16) % modulus
        recovered = pow(signature, public_exponent, modulus)
        return recovered == expected
