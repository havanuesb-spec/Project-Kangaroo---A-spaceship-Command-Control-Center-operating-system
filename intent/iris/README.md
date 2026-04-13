# Iris Intent Security

This folder provides an iris-backed registration and access layer.

Components:
- `registration.py`: iris entry and deletion in a double-secure library.
- `access.py`: RSA-digest-based access checks.
- `rsa_hash.py`: lightweight digest and modular verification helpers.
- `double_secure_iris_library_registration/`: canonical and working registry copies.

Notes:
- the library is backed by the security guard for erase/tamper recovery.
- the RSA flow is a scaffold for controlled access, not a production biometric matcher.
