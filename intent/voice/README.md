# Voice Intent Security

This folder provides a voice-backed registration, access, and timbre-coherence layer.

Components:
- `registration.py`: voice entry and deletion in the registration library.
- `access.py`: RSA-digest-based access checks for registered voice identities.
- `timbre_coherence.py`: voice timbre anomaly and coherence scoring.
- `voice_library_registration/`: canonical and working registry copies.

Notes:
- the timbre engine estimates mismatch and instability for review.
- it does not determine whether a speaker is lying.
